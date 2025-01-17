import os
import sys
import numpy as np
import paddle as pdpd


#print numpy array like C structure
def print_alike(arr):
    shape = arr.shape
    rank = len(shape)
    #print("shape: ", shape, "rank: %d" %(rank))

    #for idx, value in np.ndenumerate(arr):
    #    print(idx, value)
    
    def print_array(arr, end=' '):
        shape = arr.shape
        rank = len(arr.shape)
        if rank > 1:
            line = "{"
            for i in range(arr.shape[0]):
                line += print_array(arr[i,:], end="},\n" if i < arr.shape[0]-1 else "}")
            line += end
            return line
        else:
            line = "{"           
            for i in range(arr.shape[0]):              
                line += "{:.2f}".format(arr[i]) #str(arr[i])
                line += ", " if i < shape[0]-1 else ' '
            line += end
            #print(line)
            return line
    # print(print_array(arr, "}"))


def saveModel(name, exe, feedkeys:list, fetchlist:list, inputs:list, outputs:list, target_dir:str):
    model_dir = os.path.join(target_dir, name)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)      

    # print("\n\n------------- %s -----------\n" % (name))
    for i, input in enumerate(inputs):
        # print("INPUT %s :" % (feedkeys[i]), input.shape, input.dtype, "\n")
        # print_alike(input)
        np.save(os.path.join(model_dir, "input{}".format(i)), input)
        np.save(os.path.join(model_dir, "input{}.{}.{}".format(i, feedkeys[i], input.dtype)), input)
    # print("\n")

    for i, output in enumerate(outputs):
        # print("OUTPUT %s :" % (fetchlist[i]),output.shape, output.dtype, "\n")
        # print_alike(output)
        np.save(os.path.join(model_dir, "output{}".format(i)), output)     

    # composited model + scattered model
    pdpd.fluid.io.save_inference_model(model_dir, feedkeys, fetchlist, exe)
    pdpd.fluid.io.save_inference_model(model_dir, feedkeys, fetchlist, exe, model_filename=name+".pdmodel", params_filename=name+".pdiparams")   


'''
export dyn model, along with input and output for reference.
input_data: list of all inputs
'''
def exportModel(name, dyn_func, input_data:list, target_dir:str):
    model_dir = os.path.join(target_dir, name)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    save_path = '{}/{}'.format(model_dir, name)

    input_specs = []
    for idx, data in enumerate(input_data):
        input_name = 'input{}'.format(idx)
        input_specs.append(
            pdpd.static.InputSpec(shape=data.shape, dtype=data.dtype, name=input_name)
        )

        # dump input
        np.save(os.path.join(model_dir, "input{}".format(idx)), data)        

    pdpd.jit.save(dyn_func, save_path, input_specs)
    print('saved exported model to {}'.format(save_path))

    # infer
    model = pdpd.jit.load(save_path)

    result = model(*[input[:] for input in input_data])
   
    # dump output for reference
    if isinstance(result, (tuple, list)):
        for idx, out in enumerate(result):
            np.save(os.path.join(model_dir, "output{}".format(idx)), out.numpy())
    else:       
        np.save(os.path.join(model_dir, "output{}".format(0)), result.numpy())


if __name__ == "__main__":
    np.set_printoptions(precision=2)
    np.set_printoptions(suppress=True)  

    #x = np.random.randn(2,3).astype(np.float32)
    x = np.array([[[
        [1, 2, 3],
        [4, 5, 6]
    ],
    [
        [1, 2, 3],
        [4, 5, 6]
    ]], 
    [[
        [1, 2, 3],
        [4, 5, 6]
    ],
    [
        [1, 2, 3],
        [4, 5, 6]
    ]]]).astype(np.float32)