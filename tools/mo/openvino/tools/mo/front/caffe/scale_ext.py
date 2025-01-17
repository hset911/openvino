# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import numpy as np

from openvino.tools.mo.front.caffe.extractors.utils import embed_input, weights_biases
from openvino.tools.mo.front.common.partial_infer.elemental import copy_shape_infer
from openvino.tools.mo.front.extractor import FrontExtractorOp
from openvino.tools.mo.ops.scale_shift import ScaleShiftOp
from openvino.tools.mo.utils.utils import NamedAttrsClass


class ScaleFrontExtractor(FrontExtractorOp):
    op = 'scale'
    enabled = True

    @classmethod
    def extract(cls, node):
        pb = node.pb
        model = node.model_pb
        param = pb.scale_param
        attrs = {
            'axis': param.axis,
        }
        
        if model is None and len(pb.bottom) == 1:
            # default weights and biases for scale layer if the caffemodel file doesn't contain them
            model = NamedAttrsClass({'blobs': np.array([NamedAttrsClass({'data': np.array([1])}),
                                                 NamedAttrsClass({'data': np.array([0])})])})
        # scale with 1 input and 1 or 2 blobs
        if model and len(model.blobs) != 0 and len(pb.bottom) == 1:
            attrs.update(weights_biases(param.bias_term, model))
        # 2 inputs + bias
        elif len(pb.bottom) == 2 and param.bias_term:
            if model is None or len(model.blobs) == 0:
                # default bias for scale layer with 2 inputs if the caffemodel file doesn't contain them
                model = NamedAttrsClass({'blobs': np.array([NamedAttrsClass({'data': np.array([0])})])})

            embed_input(attrs, 1, 'biases', model.blobs[0].data)
        ScaleShiftOp.update_node_stat(node, attrs)
        return cls.enabled

