// Copyright (C) 2018-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#include "op_table.hpp"
#include "openvino/opsets/opset8.hpp"

using namespace std;
using namespace ov::opset8;

namespace ov {
namespace frontend {
namespace tf {
namespace op {

OutputVector translate_no_op(const NodeContext& node) {
    if (node.get_input_size() == 0) {
        return OutputVector{};
    }

    TF_OP_VALIDATION_CHECK(node,
                           node.get_input_size() == 1,
                           "NoOp has " + to_string(node.get_input_size()) + " inputs, should have 1");

    auto input = node.get_input(0);
    set_out_name(node.get_name(), input);
    set_out_name(node.get_name() + ":" + "0", input);
    return {input};
}
}  // namespace op
}  // namespace tf
}  // namespace frontend
}  // namespace ov