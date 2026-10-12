/*
 * This file is part of the DiscoPoP software
 * (http://www.discopop.tu-darmstadt.de)
 *
 * Copyright (c) 2020, Technische Universitaet Darmstadt, Germany
 *
 * This software may be modified and distributed under the terms of
 * the 3-Clause BSD License. See the LICENSE file in the package base
 * directory for details.
 *
 */

#include "../DiscoPoP.hpp"

unsigned DiscoPoP::dp_reduction_get_file_id(llvm::Function *func) {
  unsigned file_id = 0;

  // get the filepath of this function
  char abs_path[PATH_MAX] = {'\0'};
  for (auto bb_it = func->begin(); bb_it != func->end(); ++bb_it) {
    for (auto instr_it = bb_it->begin(); instr_it != bb_it->end(); ++instr_it) {
      llvm::MDNode *node = instr_it->getMetadata("dbg");
      if (!node)
        continue;

      llvm::DILocation *di_loc = llvm::dyn_cast<llvm::DILocation>(node);
      llvm::StringRef filename = di_loc->getFilename();
      llvm::StringRef directory = di_loc->getDirectory();

      char *success = realpath((directory.str() + "/" + filename.str()).c_str(), abs_path);
      if (!success) {
        realpath(filename.str().c_str(), abs_path);
      }

      break;
    }
    if (abs_path[0] != '\0')
      break;
  }

  if (abs_path[0] != '\0') {
    auto it = path_to_id_.find(std::string(abs_path));
    if (it != path_to_id_.end()) {
      file_id = it->second;
    } else {
    }
  }

  return file_id;
}

// finds the previous use of 'val'
llvm::Instruction *DiscoPoP::dp_reduction_get_prev_use(llvm::Instruction *instr, llvm::Value *val) {
  if (!instr)
    return nullptr;

  auto instr_users = val->users();
  bool instr_found = false;
  for (auto user : instr_users) {
    if (!llvm::isa<llvm::Instruction>(user)) {
      continue;
    }
    llvm::Instruction *usr_instr = llvm::cast<llvm::Instruction>(user);

    if (instr_found) {
      return usr_instr;
    } else if (usr_instr == instr) {
      instr_found = true;
      continue;
    }
  }
  return llvm::dyn_cast<llvm::Instruction>(val);
}

int DiscoPoP::dp_reduction_get_op_order(char c) {
  if (c == '*' || c == '/')
    return 5;
  if (c == '+' || c == '-')
    return 4;
  if (c == '&')
    return 3;
  if (c == '^')
    return 2;
  if (c == '|')
    return 1;
  return 0;
}

Type *DiscoPoP::dp_reduction_pointsToStruct(PointerType *PTy) {
  assert(PTy);
  // (2025-10-30) Omitted check for struct type for llvm 19 compatibility
  Type *structType = PTy;
/*  if (PTy->getTypeID() == Type::PointerTyID) {
    while (structType->getTypeID() == Type::PointerTyID) {
      structType = cast<PointerType>(structType)->getPointerElementType();
    }
  }
*/
  return structType->getTypeID() == Type::StructTyID ? structType : NULL;
}

string DiscoPoP::findStructMemberName_static(MDNode *structNode, unsigned idx, IRBuilder<> &builder) {
  assert(structNode);
  assert(structNode->getOperand(10));
  MDNode *memberListNodes = cast<MDNode>(structNode->getOperand(10));
  if (idx < memberListNodes->getNumOperands()) {
    assert(memberListNodes->getOperand(idx));
    MDNode *member = cast<MDNode>(memberListNodes->getOperand(idx));
    if (member->getOperand(3)) {
      getOrInsertVarName_static(dyn_cast<MDString>(member->getOperand(3))->getString().str(), builder);
      return dyn_cast<MDString>(member->getOperand(3))->getString().str();
    }
  }
  return NULL;
}

// returns the value that the GetElementPtrInst ultimately points to
llvm::Value *DiscoPoP::dp_reduction_points_to_var(llvm::GetElementPtrInst *instr) {
  llvm::Value *points_to = nullptr;
  while (instr) {
    points_to = instr->getPointerOperand();
    instr = llvm::dyn_cast<llvm::GetElementPtrInst>(points_to);
  }
  return points_to;
}

// Encode the fileID and line number of BI as LID.
// This is needed to support multiple files in a project.
LID DiscoPoP::dp_reduction_getLID(Instruction *BI, int32_t &fileID) {
  int32_t lno;

  const DebugLoc &location = BI->getDebugLoc();
  if (location) {
    lno = BI->getDebugLoc().getLine();
  } else {
    lno = 0;
  }

  if (lno == 0) {
    return 0;
  }
  LID lid = lno;
  return lid;
}

bool DiscoPoP::dp_reduction_sanityCheck(BasicBlock *BB, int file_id) {
  LID lid;
  for (BasicBlock::iterator BI = BB->begin(), EI = BB->end(); BI != EI; ++BI) {
    lid = dp_reduction_getLID(&*BI, file_id);
    if (lid > 0) {
      return true;
    }
  }
  return false;
}

// returns a char describing the opcode, e.g. '+' for Add or FAdd
// switches + and - if a negative constant is added or subtracted
//(mainly used to support -- as reduction operation, might be implemented as
//'add -1')
char DiscoPoP::dp_reduction_get_char_for_opcode(llvm::Instruction *instr) {
  unsigned opcode = instr->getOpcode();
  if(opcode == llvm::Instruction::Call){
    // check for calls to relevant arithmetic intrinsic functions (fma, fmuladd)
    // full list of arithmetic intrinsics:
    //llvm.sqrt, llvm.fabs, llvm.powi, llvm.pow, llvm.exp, llvm.exp2, llvm.log, llvm.log2, llvm.log10, llvm.sin, llvm.cos
    //llvm.floor, llvm.ceil, llvm.trunc, llvm.rint, llvm.nearbyint, llvm.round, llvm.fma, llvm.fmuladd
    CallInst* call = dyn_cast<CallInst>(instr);
    Function* callee = call->getCalledFunction();
    if(callee && callee->getName().starts_with("llvm.")){
      // check for relevant arithmentic intrinsics which allow a specific handling
      StringRef intrinsicName = callee->getName();
      if (intrinsicName.contains("fma") || intrinsicName.contains("fmuladd")){
        bool any_operand_is_negative_constant = false;
        if (instr->getNumOperands() >= 1) {
          for(auto i = 1; i < instr->getNumOperands(); ++i){
            Value *rhs_value = instr->getOperand(i);
            if (isa<ConstantInt>(rhs_value)) {
              any_operand_is_negative_constant = cast<ConstantInt>(rhs_value)->isNegative();
            }
          }
        }

        if (any_operand_is_negative_constant)
          return '-';
        else
          return '+';
      }
    }
  }

  if (opcode == llvm::Instruction::Add || opcode == llvm::Instruction::FAdd) {
    bool operand_is_negative_constant = false;
    if (instr->getNumOperands() >= 1) {
      Value *rhs_value = instr->getOperand(1);
      if (isa<ConstantInt>(rhs_value)) {
        operand_is_negative_constant = cast<ConstantInt>(rhs_value)->isNegative();
      }
    }

    if (operand_is_negative_constant)
      return '-';
    else
      return '+';
  }
  if (opcode == llvm::Instruction::Sub || opcode == llvm::Instruction::FSub) {
    bool operand_is_negative_constant = false;
    if (instr->getNumOperands() >= 1) {
      Value *rhs_value = instr->getOperand(1);
      if (isa<ConstantInt>(rhs_value)) {
        operand_is_negative_constant = cast<ConstantInt>(rhs_value)->isNegative();
      }
    }

    if (operand_is_negative_constant)
      return '+';
    else
      return '-';
  }
  if (opcode == llvm::Instruction::Mul || opcode == llvm::Instruction::FMul)
    return '*';
  if (opcode == llvm::Instruction::And)
    return '&';
  if (opcode == llvm::Instruction::Or)
    return '|';
  if (opcode == llvm::Instruction::Xor)
    return '^';
  return ' ';
}

// returns true if 'value' is computed from the variable at the address 'variable': a load of it, or its address
// itself (handed to a call, for example), anywhere among the operands
bool DiscoPoP::dp_reduction_reads_variable(llvm::Value *value, llvm::Value *variable, std::set<llvm::Value *> &visited) {
  if (!value || !variable)
    return false;
  if (value == variable)
    return true;
  if (!visited.insert(value).second)
    return false;
  if (llvm::LoadInst *load = llvm::dyn_cast<llvm::LoadInst>(value)) {
    if (load->getPointerOperand() == variable)
      return true;
  }
  llvm::Instruction *instr = llvm::dyn_cast<llvm::Instruction>(value);
  if (!instr)
    return false; // a constant, a function argument, a global
  for (unsigned i = 0; i < instr->getNumOperands(); ++i) {
    if (dp_reduction_reads_variable(instr->getOperand(i), variable, visited))
      return true;
  }
  return false;
}

// returns the operation of a reduction found by the minimum / maximum heuristic of instrument_loop, read from the
// stored value: '<' for a minimum, '>' for a maximum, and ' ' where the direction cannot be read -- the caller
// then reports no reduction.
// The direction can be read where the stored value, looked at through type conversions, is a call of a minimum or
// maximum function (fmin / fmax, fminf / fmaxf, fminl / fmaxl or one of the intrinsics llvm.minnum / maxnum,
// llvm.minimum / maximum, llvm.minimumnum / maximumnum, llvm.smin / smax, llvm.umin / umax), the loaded value of
// the variable is one of its arguments (directly or through a conversion), and no other argument reads the
// variable: x = fmin(x, a[i]), x = fmax(fabs(a[i]), x).
// Everything else that the heuristic used to report as a maximum is not a reduction it can name: another function
// of the variable (x = hypot(x, a[i]), a helper that computes a minimum), a division (x = x / a[i]), a copy
// (a[i] = a[0]), a maximum with the variable in both arguments (x = fmax(x, x + a[i])).
char DiscoPoP::dp_reduction_get_min_max_char(llvm::StoreInst *store_instr, llvm::LoadInst *load_instr) {
  if (!store_instr || !load_instr)
    return ' ';

  // look through type conversions of the stored value, e.g. x = (float) fmin(x, a[i])
  llvm::Value *stored_value = store_instr->getValueOperand();
  while (llvm::isa<llvm::CastInst>(stored_value)) {
    stored_value = llvm::cast<llvm::CastInst>(stored_value)->getOperand(0);
  }

  llvm::CallInst *call = llvm::dyn_cast<llvm::CallInst>(stored_value);
  if (!call)
    return ' ';
  llvm::Function *callee = call->getCalledFunction();
  if (!callee)
    return ' ';

  llvm::StringRef name = callee->getName();
  bool is_minimum = name == "fmin" || name == "fminf" || name == "fminl" || name.starts_with("llvm.minnum.") ||
                    name.starts_with("llvm.minimum.") || name.starts_with("llvm.minimumnum.") ||
                    name.starts_with("llvm.smin.") || name.starts_with("llvm.umin.");
  bool is_maximum = name == "fmax" || name == "fmaxf" || name == "fmaxl" || name.starts_with("llvm.maxnum.") ||
                    name.starts_with("llvm.maximum.") || name.starts_with("llvm.maximumnum.") ||
                    name.starts_with("llvm.smax.") || name.starts_with("llvm.umax.");
  if (!is_minimum && !is_maximum)
    return ' ';

  // exactly one of the arguments has to be the loaded value of the reduction variable ...
  llvm::Value *variable = store_instr->getPointerOperand();
  int carrying_argument = -1;
  for (unsigned i = 0; i < call->arg_size(); ++i) {
    llvm::Value *argument = call->getArgOperand(i);
    while (llvm::isa<llvm::CastInst>(argument)) {
      argument = llvm::cast<llvm::CastInst>(argument)->getOperand(0);
    }
    llvm::LoadInst *argument_load = llvm::dyn_cast<llvm::LoadInst>(argument);
    if (argument == load_instr || (argument_load && argument_load->getPointerOperand() == variable)) {
      if (carrying_argument != -1)
        return ' ';
      carrying_argument = i;
    }
  }
  if (carrying_argument == -1)
    return ' ';

  // ... and no other argument may read the variable
  for (unsigned i = 0; i < call->arg_size(); ++i) {
    if ((int)i == carrying_argument)
      continue;
    std::set<llvm::Value *> visited;
    if (dp_reduction_reads_variable(call->getArgOperand(i), variable, visited))
      return ' ';
  }
  return is_minimum ? '<' : '>';
}

// return true if 'operand' is an operand of the instruction 'instr'
bool DiscoPoP::dp_reduction_is_operand(llvm::Instruction *instr, llvm::Value *operand) {
  unsigned num_operands = instr->getNumOperands();
  for (unsigned i = 0; i < num_operands; ++i) {
    if (instr->getOperand(i) == operand)
      return true;
  }
  return false;
}

bool DiscoPoP::dp_reduction_init_util(std::string fmap_path) {
  std::ifstream fmap_file;
  fmap_file.open(fmap_path.c_str());
  if (fmap_file.fail()) {
    std::cout << "Opening FileMapping failed: " << strerror(errno) << "\n";
  }
  if (!fmap_file.is_open()) {
    return false;
  }

  std::string line;
  while (std::getline(fmap_file, line)) {
    char filename[512] = {'\0'};
    int file_id = 0;

    int cnt = sscanf(line.c_str(), "%d\t%s", &file_id, filename);
    if (cnt == 2) {

      path_to_id_.emplace(std::string(filename), file_id);
    }
  }

  fmap_file.close();

  return true;
}
