# ONNX Runtime Web Demo

ONNX Runtime Web demo is an interactive demo portal showing real use cases running [ONNX Runtime Web](https://github.com/microsoft/onnxruntime/tree/master/js/web#readme) in VueJS. It currently supports four examples for you to quickly experience the power of ONNX Runtime Web.

The demo is available here [ONNX Runtime Web demo website](https://microsoft.github.io/onnxruntime-web-demo/).

_NOTE: Currently, the supported platforms are Edge/Chrome/Firefox/Electron/Node.js (support for other platforms is coming soon)._

## Use Cases

### MNIST

[MNIST](https://github.com/onnx/models/tree/master/vision/classification/mnist) is a convolutional neural network that predicts handwritten digits. In the demo, you can draw any number on the canvas and the model will tell you what number it is!

## Run ONNX Runtime Web Demo

### Install Dependencies

```
npm install
```

### Serve the demo

**Serve the demo in localhost**

```
npm run serve
```

This will start a dev server and run ONNX Runtime Web demo on your localhost.

### Deploy the demo

```
npm run build
```

This will pack the source files into `/docs` folder and be ready for deployment.

## Credits

This demo is adapted from [keras.js demo](https://github.com/transcranial/keras-js). Modifications have been made to the UI and the backend uses `ONNX Runtime Web`.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
