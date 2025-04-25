"""
A complete neural network implementation with convolutional, pooling and
activation layers.

This module contains classes for building CNNs, including:
- Convolutional layers with configurable padding/strides
- Max pooling layers with dynamic window sizing
- Parametric ReLU activation layers
- Fully connected layers

The implementation supports both forward propagation and backward gradient
computation.
"""

from typing import Optional
import numpy as np
from keras.src.datasets import mnist


class TensorSize:
    """Stores 3D tensor dimensions (channels, height, width) for layer
    configuration."""

    def __init__(
        self,
        depth: int = 0,
        height: int = 0,
        width: int = 0
    ):
        """
        Dimensions container for neural network tensors.

        Args:
            depth: Number of feature channels
            height: Spatial height dimension
            width: Spatial width dimension
        """
        self.depth = depth
        self.height = height
        self.width = width


class Tensor:
    """Data container with values and associated dimensional metadata."""

    def __init__(
        self,
        size: TensorSize = TensorSize(),
        values: Optional[np.ndarray] = None
    ):
        """
        Initialize tensor with specified dimensions.

        Args:
            size: Tensor dimensions as TensorSize object
            values: Optional numpy array (reshaped to match dimensions)
        """
        self.size = size
        if values is None:
            self.values = np.zeros((size.depth, size.height, size.width))
        else:
            self.values = values.reshape((size.depth, size.height, size.width))


class ConvLayer:
    """Convolutional layer with learnable filters and configurable geometry."""

    def __init__(
        self,
        size: TensorSize = TensorSize(),
        filters_count: int = 0,
        filters_size: int = 0,
        padding: int = 0,
        step: int = 1
    ):
        """
        Initialize convolutional layer.

        Args:
            size: Input tensor dimensions
            filters_count: Number of filters in the layer
            filters_size: Size of each filter (square)
            padding: Padding to add to input
            step: Stride for convolution operation
        """
        self.input_size = size
        self.output_size = TensorSize(
            filters_count,
            int((size.height - filters_size + 2 * padding) / step + 1),
            int((size.width - filters_size + 2 * padding) / step + 1)
        )
        self.padding = padding
        self.step = step
        self.filters_count = filters_count
        self.filters_size = filters_size
        self.filters_depth = size.depth
        self.weights = np.random.normal(
            loc=0.0,
            scale=np.sqrt(
                2.0
                / (
                    self.filters_size
                    * self.filters_size
                    * self.filters_depth
                )
            ),
            size=(filters_count, size.depth, filters_size, filters_size)
        )
        self.biases = np.full((filters_count), 0.01, dtype=float)
        self.weights_gradients = np.zeros_like(self.weights)
        self.biases_gradients = np.zeros_like(self.biases)

    def forward(self, input_tensor: Tensor) -> Tensor:
        """
        Perform forward pass through the convolutional layer.

        Args:
            input_tensor: Input tensor to convolve

        Returns:
            Output tensor after convolution
        """
        padded_input = np.pad(
            input_tensor.values,
            (
                (0, 0),
                (self.padding, self.padding),
                (self.padding, self.padding)
            ),
            mode='constant'
        )
        output_tensor = Tensor(self.output_size)

        for f in range(self.filters_count):
            for y in range(self.output_size.height):
                for x in range(self.output_size.width):
                    region = padded_input[
                        :,
                        y * self.step:y * self.step + self.filters_size,
                        x * self.step:x * self.step + self.filters_size
                    ]
                    output_tensor.values[f, y, x] = (
                        np.sum(region * self.weights[f]) + self.biases[f]
                    )
        return output_tensor

    def backward(self, dout: Tensor, input_tensor: Tensor) -> Tensor:
        """
        Perform backward pass through the convolutional layer.

        Args:
            dout: Gradient from the next layer
            input_tensor: Input tensor from forward pass

        Returns:
            Input gradient tensor with shape matching original input
        """
        padded_input = np.pad(
            input_tensor.values,
            (
                (0, 0),
                (self.padding, self.padding),
                (self.padding, self.padding)
            ),
            mode='constant'
        )
        padded_input_grad = np.zeros_like(padded_input)

        for f in range(self.filters_count):
            for y in range(self.output_size.height):
                for x in range(self.output_size.width):
                    region = padded_input[
                        :,
                        y * self.step:y * self.step + self.filters_size,
                        x * self.step:x * self.step + self.filters_size
                    ]
                    self.weights_gradients[f] += dout.values[f, y, x] * region
                    self.biases_gradients[f] += dout.values[f, y, x]
                    padded_input_grad[
                        :,
                        y * self.step:y * self.step + self.filters_size,
                        x * self.step:x * self.step + self.filters_size
                    ] += dout.values[f, y, x] * self.weights[f]

        input_grad = padded_input_grad[
            :,
            self.padding:-self.padding if self.padding > 0 else None,
            self.padding:-self.padding if self.padding > 0 else None
        ]
        return Tensor(self.input_size, input_grad)

    def update_weights(self, learning_rate: float):
        """
        Update weights and biases using accumulated gradients.

        Args:
            learning_rate: Learning rate for weight updates
        """
        self.weights -= learning_rate * self.weights_gradients
        self.biases -= learning_rate * self.biases_gradients
        self.weights_gradients.fill(0)
        self.biases_gradients.fill(0)


class MaxPoolingLayer:
    """Implements a max pooling layer for downsampling."""
    def __init__(self, size: TensorSize = TensorSize(), scale: float = 1.0):
        """
        Initialize max pooling layer.

        Args:
            size: Input tensor dimensions
            scale: Scaling factor
        """

        self.input_size = size
        self.scale = scale
        # Calculate output dimensions with ceiling using integer arithmetic
        self.output_size = TensorSize(
            size.depth,
            int((size.height + scale - 1) // scale),
            int((size.width + scale - 1) // scale)
        )
        self.mask = np.zeros((size.depth, size.height, size.width))

    def forward(self, input_tensor: Tensor) -> Tensor:
        """
        Perform forward pass through the max pooling layer.

        Args:
            input_tensor: Input tensor to pool

        Returns:
            Output tensor after max pooling
        """
        input_depth = self.input_size.depth
        input_height = self.input_size.height
        input_width = self.input_size.width
        output_height = self.output_size.height
        output_width = self.output_size.width

        # Calculate window dimensions
        window_h = int(np.ceil(input_height / output_height))
        window_w = int(np.ceil(input_width / output_width))

        output_tensor = Tensor(self.output_size)
        self.mask = np.zeros_like(input_tensor.values)

        for d in range(input_depth):
            for i in range(output_height):
                # Calculate vertical boundaries
                start_h = int(i * (input_height / output_height))
                end_h = min(start_h + window_h, input_height)

                for j in range(output_width):
                    # Calculate horizontal boundaries
                    start_w = int(j * (input_width / output_width))
                    end_w = min(start_w + window_w, input_width)

                    # Extract region and find max
                    region = input_tensor.values[
                        d,
                        start_h:end_h,
                        start_w:end_w
                    ]
                    max_val = np.max(region)
                    output_tensor.values[d, i, j] = max_val

                    # Record position of max value
                    max_pos = np.unravel_index(region.argmax(), region.shape)
                    self.mask[
                        d,
                        start_h + max_pos[0],
                        start_w + max_pos[1]
                    ] = 1

        return output_tensor

    def backward(self, dout: Tensor) -> Tensor:
        """
        Perform backward pass through the max pooling layer.

        Args:
            dout: Gradient from the next layer

        Returns:
            Gradient with respect to input
        """
        input_depth = self.input_size.depth
        output_height = self.output_size.height
        output_width = self.output_size.width
        input_height = self.input_size.height
        input_width = self.input_size.width

        # Calculate window dimensions (same as forward pass)
        window_h = int(np.ceil(input_height / output_height))
        window_w = int(np.ceil(input_width / output_width))

        output_tensor = Tensor(self.input_size)

        for d in range(input_depth):
            for i in range(output_height):
                start_h = int(i * (input_height / output_height))
                end_h = min(start_h + window_h, input_height)

                for j in range(output_width):
                    start_w = int(j * (input_width / output_width))
                    end_w = min(start_w + window_w, input_width)

                    # Propagate gradient through max position
                    output_tensor.values[d, start_h:end_h, start_w:end_w] += \
                        dout.values[d, i, j]\
                        * self.mask[
                            d,
                            start_h:end_h,
                            start_w:end_w
                        ]

        return output_tensor


class PReLULayer:
    """Implements a Parametric Rectified Linear Unit (PReLU) activation layer.
    """

    def __init__(self, size: TensorSize, init: float = 0.25):
        """
        Initialize PReLU layer.

        Args:
            size: Input tensor dimensions
            init: Initial value for alpha parameter
        """
        self.size = size
        self.alpha = np.full((size.depth, 1, 1), init, dtype=np.float32)
        self.grad_alpha = np.zeros_like(self.alpha)

    def forward(self, input_tensor: Tensor) -> Tensor:
        """
        Perform forward pass through PReLU activation.

        Args:
            input_tensor: Input tensor

        Returns:
            Output tensor after PReLU
        """
        output = Tensor(self.size)
        output.values = np.maximum(input_tensor.values, 0) + \
            self.alpha * np.minimum(input_tensor.values, 0)
        return output

    def backward(self, dout: Tensor, input_tensor: Tensor) -> Tensor:
        """
        Perform backward pass through PReLU activation.

        Args:
            dout: Gradient from next layer
            input_tensor: Input tensor from forward pass

        Returns:
            Gradient with respect to input
        """
        mask = input_tensor.values <= 0
        tensor_output = Tensor(self.size)
        tensor_output.values = dout.values * np.where(mask, self.alpha, 1)

        self.grad_alpha = np.sum(
            dout.values * input_tensor.values * mask,
            axis=(1, 2),
            keepdims=True
        )

        return tensor_output

    def update_alpha(self, learning_rate: float):
        """
        Update alpha parameters using accumulated gradients.

        Args:
            learning_rate: Learning rate for alpha updates
        """
        self.alpha -= learning_rate * self.grad_alpha
        self.grad_alpha.fill(0)


class FullyConnectionedLayer:
    """Implements fully connected layer (dense layer)."""
    def __init__(self, size: TensorSize, outputs: int):
        """
        Configure dense layer parameters.

        Args:
            size: Input tensor dimensions
            outputs: Number of output neurons
        """
        self.input_size = size
        self.output_size = TensorSize(1, 1, outputs)

        fan_in = size.depth * size.height * size.width
        self.weights = np.random.normal(
            0,
            np.sqrt(2/fan_in),
            (outputs, fan_in)
        )
        self.biases = np.full(outputs, 0.01)
        self.weights_grad = np.zeros_like(self.weights)
        self.biases_grad = np.zeros_like(self.biases)

    def forward(self, x: Tensor) -> Tensor:
        """
        Perform affine transformation (Wx + b).

        Args:
            x: Input tensor with arbitrary dimensions

        Returns:
            Output tensor with shape (1, 1, outputs)
        """
        output = Tensor(self.output_size)
        flattened = x.values.flatten()
        output.values[0, 0, :] = np.dot(self.weights, flattened) + self.biases
        return output

    def backward(self, dout: Tensor, input_tensor: Tensor) -> Tensor:
        """
        Compute gradients for weights, biases and input.

        Args:
            dout: Gradient tensor from next layer
            input_tensor: Original input from forward pass

        Returns:
            Input gradient tensor
        """
        flat_input = input_tensor.values.flatten()
        self.weights_grad += np.outer(dout.values[0, 0, :], flat_input)
        self.biases_grad += dout.values[0, 0, :]

        input_grad: np.ndarray = np.dot(self.weights.T, dout.values[0, 0, :])
        return Tensor(
            self.input_size,
            input_grad.reshape(
                input_tensor.values.shape
            )
        )

    def update(self, learning_rate: float):
        """
        Update parameters using accumulated gradients.

        Args:
            learning_rate: Scaling factor for weight updates
        """
        self.weights -= learning_rate * self.weights_grad
        self.biases -= learning_rate * self.biases_grad
        self.weights_grad.fill(0)
        self.biases_grad.fill(0)


def soft_max(arr: np.ndarray) -> np.ndarray:
    """
    Compute numerically stable softmax probabilities.

    Args:
        arr: Input logits array

    Returns:
        Probability distribution over classes
    """
    exp = np.exp(arr)
    return exp / exp.sum()


class AI:
    """Main neural network architec$4$ture for MNIST classification."""
    def __init__(self):
        """
        Initialize CNN architecture with sequence:
        input →
        [Conv16(3x3) → PReLU]x2 → MaxPool(2x2) →
        [Conv32(3x3) → PReLU]x2 → MaxPool(2x2) →
        FC128 → PReLU → FC10 → PReLU → SoftMax →
        output
        """
        # Input and output tensor size
        self.input_size = TensorSize(1, 28, 28)
        self.output_size = TensorSize(1, 1, 10)

        # First convolution block
        self.I_CONV16C3 = ConvLayer(self.input_size, 16, 3)  # 16 filters 3x3
        self.II_PReLU = PReLULayer(self.I_CONV16C3.output_size)

        # Second convolution block
        self.III_CONV16C3 = ConvLayer(self.II_PReLU.size, 16, 3)
        self.IV_PReLU = PReLULayer(self.III_CONV16C3.output_size)
        self.V_MAXPOOL = MaxPoolingLayer(self.IV_PReLU.size, 2)  # 2x2 pooling

        # Third convolution block
        self.VI_CONV32C3 = ConvLayer(self.V_MAXPOOL.output_size, 32, 3)
        self.VII_PReLU = PReLULayer(self.VI_CONV32C3.output_size)

        # Fourth convolution block
        self.VIII_CONV32C3 = ConvLayer(self.VII_PReLU.size, 32, 3)
        self.IX_PReLU = PReLULayer(self.VIII_CONV32C3.output_size)
        self.X_MAXPOOL = MaxPoolingLayer(self.IX_PReLU.size, 2)

        # Final classification layers
        self.XI_FC128 = FullyConnectionedLayer(self.X_MAXPOOL.output_size, 128)
        self.XII_PReLU = PReLULayer(self.XI_FC128.output_size)
        self.XIII_FC10 = FullyConnectionedLayer(self.XII_PReLU.size, 10)
        self.XIV_PReLU = PReLULayer(self.XIII_FC10.output_size)

    class Stats:
        """Stores intermediate layer results for debugging/analysis."""
        def __init__(self):
            """
            Initialize storage for network layer inputs/outputs.
            """
            self.input: np.ndarray

            # First convolution block
            self.I_CONV16C3_result: Tensor
            self.II_PReLU_result: Tensor

            # Second convolution block
            self.III_CONV16C3_result: Tensor
            self.IV_PReLU_result: Tensor
            self.V_MAXPOOL_result: Tensor

            # Third convolution block
            self.VI_CONV32C3_result: Tensor
            self.VII_PReLU_result: Tensor

            # Fourth convolution block
            self.VIII_CONV32C3_result: Tensor
            self.IX_PReLU_result: Tensor
            self.X_MAXPOOL_result: Tensor

            # Final classification layers
            self.XI_FC128_result: Tensor
            self.XII_PReLU_result: Tensor
            self.XIII_FC10_result: Tensor
            self.XIV_PReLU_result: Tensor

            self.output: np.ndarray

    def main(self, img: np.ndarray):
        """Perform forward pass through entire network.

        Args:
            img: Input image array (28x28 pixels)

        Returns:
            Output logits for 10 digit classes
        """
        # Layer-by-layer forward propagation
        return soft_max(
          self.XIV_PReLU.forward(
            self.XIII_FC10.forward(
              self.XII_PReLU.forward(
                self.XI_FC128.forward(
                  self.X_MAXPOOL.forward(
                    self.IX_PReLU.forward(
                      self.VIII_CONV32C3.forward(
                        self.VII_PReLU.forward(
                          self.VI_CONV32C3.forward(
                            self.V_MAXPOOL.forward(
                              self.IV_PReLU.forward(
                                self.III_CONV16C3.forward(
                                  self.II_PReLU.forward(
                                    self.I_CONV16C3.forward(
                                      Tensor(
                                        self.input_size,
                                        img
                                      )
                                    )
                                  )
                                )
                              )
                            )
                          )
                        )
                      )
                    )
                  )
                )
              )
            )
          ).values.reshape((10))
        )

    def forward(self, img: np.ndarray) -> Stats:
        """Perform forward pass through entire network.

        Args:
            img: Input image array (28x28 pixels)

        Returns:
            Output logits for 10 digit classes
        """
        forward_stats = self.Stats()
        forward_stats.input = img
        forward_stats.I_CONV16C3_result = self.I_CONV16C3.forward(
            Tensor(self.input_size, forward_stats.input)
        )
        forward_stats.II_PReLU_result = self.II_PReLU.forward(
            forward_stats.I_CONV16C3_result
        )
        forward_stats.III_CONV16C3_result = self.III_CONV16C3.forward(
            forward_stats.II_PReLU_result
        )
        forward_stats.IV_PReLU_result = self.IV_PReLU.forward(
            forward_stats.III_CONV16C3_result
        )
        forward_stats.V_MAXPOOL_result = self.V_MAXPOOL.forward(
            forward_stats.IV_PReLU_result
        )
        forward_stats.VI_CONV32C3_result = self.VI_CONV32C3.forward(
            forward_stats.V_MAXPOOL_result
        )
        forward_stats.VII_PReLU_result = self.VII_PReLU.forward(
            forward_stats.VI_CONV32C3_result
        )
        forward_stats.VIII_CONV32C3_result = self.VIII_CONV32C3.forward(
            forward_stats.VII_PReLU_result
        )
        forward_stats.IX_PReLU_result = self.IX_PReLU.forward(
            forward_stats.VIII_CONV32C3_result
        )
        forward_stats.X_MAXPOOL_result = self.X_MAXPOOL.forward(
           forward_stats.IX_PReLU_result
        )
        forward_stats.XI_FC128_result = self.XI_FC128.forward(
            forward_stats.X_MAXPOOL_result
        )
        forward_stats.XII_PReLU_result = self.XII_PReLU.forward(
            forward_stats.XI_FC128_result
        )
        forward_stats.XIII_FC10_result = self.XIII_FC10.forward(
            forward_stats.XII_PReLU_result
        )
        forward_stats.XIV_PReLU_result = self.XIV_PReLU.forward(
            forward_stats.XIII_FC10_result
        )
        forward_stats.output = soft_max(
            forward_stats.XIV_PReLU_result.values
        )
        return forward_stats

    def backward(self, img: np.ndarray, answer: np.uint8):
        """Perform backward pass through entire network.

        Args:
            img: Input image array (28x28 pixels)

        Returns:
            None
        """
        forward_stats = self.forward(img)
        backward_stats = self.Stats()
        backward_stats.input = np.zeros((1, 1, 10))
        backward_stats.input = forward_stats.output.copy()
        backward_stats.input[0, 0, answer] -= 1.0
        backward_stats.XIV_PReLU_result = self.XIV_PReLU.backward(
            Tensor(self.output_size, backward_stats.input),
            forward_stats.XIII_FC10_result
        )
        backward_stats.XIII_FC10_result = self.XIII_FC10.backward(
            backward_stats.XIV_PReLU_result,
            forward_stats.XII_PReLU_result
        )
        backward_stats.XII_PReLU_result = self.XII_PReLU.backward(
            backward_stats.XIII_FC10_result,
            forward_stats.XI_FC128_result
        )
        backward_stats.XI_FC128_result = self.XI_FC128.backward(
            backward_stats.XII_PReLU_result,
            forward_stats.X_MAXPOOL_result
        )
        backward_stats.X_MAXPOOL_result = self.X_MAXPOOL.backward(
            backward_stats.XI_FC128_result
        )
        backward_stats.IX_PReLU_result = self.IX_PReLU.backward(
            backward_stats.X_MAXPOOL_result,
            forward_stats.VIII_CONV32C3_result
        )
        backward_stats.VIII_CONV32C3_result = self.VIII_CONV32C3.backward(
            backward_stats.IX_PReLU_result,
            forward_stats.VII_PReLU_result
        )
        backward_stats.VII_PReLU_result = self.VII_PReLU.backward(
            backward_stats.VIII_CONV32C3_result,
            forward_stats.VI_CONV32C3_result
        )
        backward_stats.VI_CONV32C3_result = self.VI_CONV32C3.backward(
            backward_stats.VII_PReLU_result,
            forward_stats.V_MAXPOOL_result
        )
        backward_stats.V_MAXPOOL_result = self.V_MAXPOOL.backward(
            backward_stats.VI_CONV32C3_result
        )
        backward_stats.IV_PReLU_result = self.IV_PReLU.backward(
            backward_stats.V_MAXPOOL_result,
            forward_stats.III_CONV16C3_result
        )
        backward_stats.III_CONV16C3_result = self.III_CONV16C3.backward(
            backward_stats.IV_PReLU_result,
            forward_stats.II_PReLU_result
        )
        backward_stats.II_PReLU_result = self.II_PReLU.backward(
            backward_stats.III_CONV16C3_result,
            forward_stats.I_CONV16C3_result
        )
        backward_stats.I_CONV16C3_result = self.I_CONV16C3.backward(
            backward_stats.II_PReLU_result,
            Tensor(self.input_size, forward_stats.input)
        )
        return backward_stats

    def update(self, learning_rate: float):
        """
        Update parameters using accumulated gradients.

        Args:
            learning_rate: Scaling factor for weight updates
        """
        self.I_CONV16C3.update_weights(learning_rate)
        self.II_PReLU.update_alpha(learning_rate)
        self.III_CONV16C3.update_weights(learning_rate)
        self.IV_PReLU.update_alpha(learning_rate)
        self.VI_CONV32C3.update_weights(learning_rate)
        self.VII_PReLU.update_alpha(learning_rate)
        self.VIII_CONV32C3.update_weights(learning_rate)
        self.IX_PReLU.update_alpha(learning_rate)
        self.XI_FC128.update(learning_rate)
        self.XII_PReLU.update_alpha(learning_rate)
        self.XIII_FC10.update(learning_rate)
        self.XIV_PReLU.update_alpha(learning_rate)

    def save_configs(self, filename: str = "AI_config.npz"):
        """
        Serialize model parameters to file.

        Args:
            filename: Output file path (.npz format)
        """
        np.savez(
            filename,
            # ConvLayer I_CONV16C3
            I_CONV16C3_weights=self.I_CONV16C3.weights,
            I_CONV16C3_biases=self.I_CONV16C3.biases,
            I_CONV16C3_weights_gradients=self.I_CONV16C3.weights_gradients,
            I_CONV16C3_biases_gradients=self.I_CONV16C3.biases_gradients,

            # PReLU II_PReLU
            II_PReLU_alpha=self.II_PReLU.alpha,
            II_PReLU_grad_alpha=self.II_PReLU.grad_alpha,

            # ConvLayer III_CONV16C3
            III_CONV16C3_weights=self.III_CONV16C3.weights,
            III_CONV16C3_biases=self.III_CONV16C3.biases,
            III_CONV16C3_weights_gradients=self.III_CONV16C3.weights_gradients,
            III_CONV16C3_biases_gradients=self.III_CONV16C3.biases_gradients,

            # PReLU IV_PReLU
            IV_PReLU_alpha=self.IV_PReLU.alpha,
            IV_PReLU_grad_alpha=self.IV_PReLU.grad_alpha,

            # ConvLayer VI_CONV32C3
            VI_CONV32C3_weights=self.VI_CONV32C3.weights,
            VI_CONV32C3_biases=self.VI_CONV32C3.biases,
            VI_CONV32C3_weights_gradients=self.VI_CONV32C3.weights_gradients,
            VI_CONV32C3_biases_gradients=self.VI_CONV32C3.biases_gradients,

            # PReLU VII_PReLU
            VII_PReLU_alpha=self.VII_PReLU.alpha,
            VII_PReLU_grad_alpha=self.VII_PReLU.grad_alpha,

            # ConvLayer VIII_CONV32C3
            VIII_CONV32C3_weights=self.VIII_CONV32C3.weights,
            VIII_CONV32C3_biases=self.VIII_CONV32C3.biases,
            VIII_CONV32C3_weights_gradients=self.
            VIII_CONV32C3.weights_gradients,
            VIII_CONV32C3_biases_gradients=self.VIII_CONV32C3.biases_gradients,

            # PReLU IX_PReLU
            IX_PReLU_alpha=self.IX_PReLU.alpha,
            IX_PReLU_alpha_grad=self.IX_PReLU.grad_alpha,

            # FullyConnected XI_FC128
            XI_FC128_weights=self.XI_FC128.weights,
            XI_FC128_biases=self.XI_FC128.biases,
            XI_FC128_weights_grad=self.XI_FC128.weights_grad,
            XI_FC128_biases_grad=self.XI_FC128.biases_grad,

            # PReLU XII_PReLU
            XII_PReLU_alpha=self.XII_PReLU.alpha,
            XII_PReLU_grad_alpha=self.XII_PReLU.grad_alpha,

            # FullyConnected XIII_FC10
            XIII_FC10_weights=self.XIII_FC10.weights,
            XIII_FC10_biases=self.XIII_FC10.biases,
            XIII_FC10_weights_grad=self.XIII_FC10.weights_grad,
            XIII_FC10_biases_grad=self.XIII_FC10.biases_grad,

            # PReLU XIV_PReLU
            XIV_PReLU_alpha=self.XIV_PReLU.alpha,
            XIV_PReLU_grad_alpha=self.XIV_PReLU.grad_alpha
        )

    def load_configs(self, filename: str = "AI_config.npz"):
        """
        Load model parameters from file.

        Args:
            filename: Input file path (.npz format)
        """
        try:
            data = np.load(filename)
        except FileNotFoundError:
            print("File doesn't exist!")

        # ConvLayer I_CONV16C3
        self.I_CONV16C3.weights = data['I_CONV16C3_weights']
        self.I_CONV16C3.biases = data['I_CONV16C3_biases']
        self.I_CONV16C3.weights_gradients =\
            data['I_CONV16C3_weights_gradients']
        self.I_CONV16C3.biases_gradients =\
            data['I_CONV16C3_biases_gradients']

        # PReLU II_PReLU
        self.II_PReLU.alpha = data['II_PReLU_alpha']
        self.II_PReLU.grad_alpha = data['II_PReLU_grad_alpha']

        # ConvLayer III_CONV16C3
        self.III_CONV16C3.weights = data['III_CONV16C3_weights']
        self.III_CONV16C3.biases = data['III_CONV16C3_biases']
        self.III_CONV16C3.weights_gradients =\
            data['III_CONV16C3_weights_gradients']
        self.III_CONV16C3.biases_gradients =\
            data['III_CONV16C3_biases_gradients']

        # PReLU IV_PReLU
        self.IV_PReLU.alpha = data['IV_PReLU_alpha']
        self.IV_PReLU.grad_alpha = data['IV_PReLU_grad_alpha']

        # ConvLayer VI_CONV32C3
        self.VI_CONV32C3.weights = data['VI_CONV32C3_weights']
        self.VI_CONV32C3.biases = data['VI_CONV32C3_biases']
        self.VI_CONV32C3.weights_gradients =\
            data['VI_CONV32C3_weights_gradients']
        self.VI_CONV32C3.biases_gradients =\
            data['VI_CONV32C3_biases_gradients']

        # PReLU VII_PReLU
        self.VII_PReLU.alpha = data['VII_PReLU_alpha']
        self.VII_PReLU.grad_alpha = data['VII_PReLU_grad_alpha']

        # ConvLayer VIII_CONV32C3
        self.VIII_CONV32C3.weights = data['VIII_CONV32C3_weights']
        self.VIII_CONV32C3.biases = data['VIII_CONV32C3_biases']
        self.VIII_CONV32C3.weights_gradients =\
            data['VIII_CONV32C3_weights_gradients']
        self.VIII_CONV32C3.biases_gradients =\
            data['VIII_CONV32C3_biases_gradients']

        # PReLU IX_PReLU
        self.IX_PReLU.alpha = data['IX_PReLU_alpha']
        self.IX_PReLU.grad_alpha = data['IX_PReLU_alpha_grad']

        # FullyConnected XI_FC128
        self.XI_FC128.weights = data['XI_FC128_weights']
        self.XI_FC128.biases = data['XI_FC128_biases']
        self.XI_FC128.weights_grad = data['XI_FC128_weights_grad']
        self.XI_FC128.biases_grad = data['XI_FC128_biases_grad']

        # PReLU XII_PReLU
        self.XII_PReLU.alpha = data['XII_PReLU_alpha']
        self.XII_PReLU.grad_alpha = data['XII_PReLU_grad_alpha']

        # FullyConnected XIII_FC10
        self.XIII_FC10.weights = data['XIII_FC10_weights']
        self.XIII_FC10.biases = data['XIII_FC10_biases']
        self.XIII_FC10.weights_grad = data['XIII_FC10_weights_grad']
        self.XIII_FC10.biases_grad = data['XIII_FC10_biases_grad']

        # PReLU XIV_PReLU
        self.XIV_PReLU.alpha = data['XIV_PReLU_alpha']
        self.XIV_PReLU.grad_alpha = data['XIV_PReLU_grad_alpha']

    def train(self, learning_rate: float = 0.001):
        """Train model on MNIST dataset

        Args:
            learning_rate: Scaling factor for weight updates
        """
        (train_X, train_y), (test_X, test_y) = mnist.load_data()
        for i in range(60000):
            self.backward(train_X[i] / 255, train_y[i])
            self.update(learning_rate)

    def test(self):
        """Test model on MNIST dataset"""
        (train_X, train_y), (test_X, test_y) = mnist.load_data()
        cnt = 0
        for i in range(10000):
            if self.main(test_X[i] / 255) == test_y[i]:
                cnt += 1
        print("Test successfull! The result is " + str(cnt / 100, 2))
