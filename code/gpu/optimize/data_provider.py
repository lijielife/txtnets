__author__ = 'mdenil'

import numpy as np

import gpu.space

import generic.optimize.data_provider

# FIXME: Integrate this with the generic BatchDataProvider
class BatchDataProvider(object):
    def __init__(self, X, Y, lengths):
        self.X = X
        self.Y = Y
        self.lengths = lengths

        self.batch_size = X.shape[0]
        self.batches_per_epoch = 1

    def next_batch(self):
        meta = {
            'lengths': self.lengths,
            'space_below': gpu.space.GPUSpace.infer(self.X, axes=['b', 'w'])
        }

        return self.X, self.Y, meta


class TransferLabelsToGPU(object):
    """
    This class doesn't actually provide GPU Xs.  It provides lists of X's on the CPU.
    It DOES describe the Xs with a GPU space though, which might be confusing.

    You're supposed to send the output of this provider into an encoder which will actually
    construct GPU matrices for your Xs.

    This class does provide Ys that live on the GPU.
    """

    def next_batch(self):
        X_batch, Y_batch, meta = super(TransferLabelsToGPU, self).next_batch()

        meta['space_below'] = gpu.space.GPUSpace(
            meta['space_below'].axes,
            meta['space_below'].extents)

        Y_batch = gpu.utils.cpu_to_gpu(Y_batch.astype(np.float32))

        return X_batch, Y_batch, meta


class LabelledSequenceMinibatchProvider(
    TransferLabelsToGPU,
    generic.optimize.data_provider.LabelledSequenceMinibatchProvider):
    pass


class LabelledSequenceBatchProvider(
    TransferLabelsToGPU,
    generic.optimize.data_provider.LabelledSequenceBatchProvider):
    pass