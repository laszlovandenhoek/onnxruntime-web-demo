<template>
  <div class="drawing-container">
    <div class="image-panel elevation-1">
      <div class="panel-content">
        <div class="panel-section" style="width: 400px">
          <div class="input-container">
            <div class="input-label">Draw any digit (0-9) here</div>
            <div class="canvas-container">
              <canvas
                id="input-canvas"
                width="300"
                height="300"
                @mousedown="activateDraw"
                @mouseup="stopDrawing"
                @mouseleave="stopDrawing"
                @mousemove="draw"
                @touchstart="activateDraw"
                @touchend="stopDrawing"
                @touchmove="draw"
              ></canvas>
            </div>

            <div class="layer-output-heading">
              <span class="layer-class">Input After Preprocessing</span>
              <br/>
              <span>28x28 grayscale</span>
            </div>
            <div class="layer-output-canvas-container">
              <canvas
                id="preprocessed-input"
                width="28"
                height="28"
                class="input-canvas"
              ></canvas>

            </div>

            <v-btn color="primary" @click="clear" style="margin: 0px">
              <v-icon icon="mdi-close" class="mr-2"></v-icon>
              Clear
            </v-btn>
          </div>
        </div>

        <div class="panel-section" style="width: 180px">
          <div class="layer-outputs-container">
            <div class="layer-output">
              <div class="layer-output-heading">
                <span class="layer-class">First Convolution Layer</span>
                <span>8 feature maps (28x28)</span>
              </div>
              <div class="layer-output-canvas-container conv1-grid">
                <canvas 
                  v-for="i in 8" 
                  :key="`conv1-${i}`"
                  :id="`conv1-${i-1}`"
                  width="28"
                  height="28"
                  class="conv1-canvas"
                ></canvas>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-section" style="width: 270px">
          <div class="layer-outputs-container">
            <div class="layer-output">
              <div class="layer-output-heading">
                <span class="layer-class">Second Convolution Layer</span>
                <span>16 feature maps (14x14)</span>
              </div>
              <div class="layer-output-canvas-container conv2-grid">
                <canvas 
                  v-for="i in 16" 
                  :key="`conv2-${i}`"
                  :id="`conv2-${i-1}`"
                  width="14"
                  height="14"
                  class="conv2-canvas"
                ></canvas>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-section" style="width: 230px">
          <div class="output-column">
            <div class="output">
              <div
                class="output-class"
                :class="{ predicted: i === predictedClass }"
                v-for="i in outputClasses"
                :key="`output-class-${i}`"
              >
                <div class="output-label">{{ i }}</div>
                <div
                  class="output-bar"
                  :style="{ width: `${Math.round(180 * output[i])}px` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
// import type { Ref } from 'vue'
import _ from "lodash";
import { mathUtils, runModelUtils } from "../../utils";
import { Tensor, InferenceSession } from "onnxruntime-web";

interface Props {
  modelFilepath: string;
  preprocess: (ctx: CanvasRenderingContext2D) => Tensor;
  postprocess: (t: Tensor) => Float32Array;
  getPredictedClass: (output: Float32Array) => number;
}

const props = withDefaults(defineProps<Props>(), {});

// State variables
const modelLoadingError = ref(false);
const sessionRunning = ref(false);
const output = ref(new Float32Array(10));
const outputClasses = ref(_.range(10));
const drawing = ref(false);
const strokes = ref<number[][][]>([]);
const inferenceTime = ref(0);
const session = ref<InferenceSession>();
const modelFile = ref(new ArrayBuffer(0));

// Computed
const predictedClass = computed(() => props.getPredictedClass(output.value));

// Methods
const initSession = async () => {
  sessionRunning.value = false;
  modelLoadingError.value = false;
  
  try {
    session.value = await runModelUtils.createModelCpu(modelFile.value);
  } catch (e) {
    throw new Error("Error: Backend not supported. ", { cause: e });
  }
  
  await runModelUtils.warmupModel(session.value!, [1, 1, 28, 28]);
};

const run = async () => {
  if (!drawing.value || sessionRunning.value) {
    return;
  }
  
  sessionRunning.value = true;
  const ctx = (
    document.getElementById("input-canvas") as HTMLCanvasElement
  ).getContext("2d", { willReadFrequently: true }) as CanvasRenderingContext2D;
  
  const tensor = props.preprocess(ctx);
  
  // Render preprocessed input
  const preprocessedCanvas = document.getElementById("preprocessed-input") as HTMLCanvasElement;
  const preprocessedCtx = preprocessedCanvas.getContext('2d')!;
  const imageData = preprocessedCtx.createImageData(28, 28);
  
  // Get tensor data and normalize for display
  const inputData = tensor.data as Float32Array;
  let min = Math.min(...Array.from(inputData));
  let max = Math.max(...Array.from(inputData));
  
  for (let i = 0; i < 28 * 28; i++) {
    const val = inputData[i];
    const normalized = Math.floor(255 * (val - min) / (max - min));
    const idx = i * 4;
    imageData.data[idx] = normalized;     // R
    imageData.data[idx + 1] = normalized; // G
    imageData.data[idx + 2] = normalized; // B
    imageData.data[idx + 3] = 255;        // A
  }
  
  preprocessedCtx.putImageData(imageData, 0, 0);

  const [res, time] = await runModelUtils.runModel(session.value!, tensor);
  output.value = props.postprocess(res["Plus214_Output_0"]);
  const conv1 = res["Plus30_output"];

  // Draw conv1 feature maps
  const conv1Data = conv1.data as Float32Array;
  for (let i = 0; i < 8; i++) {
    const canvas = document.getElementById(`conv1-${i}`) as HTMLCanvasElement;
    const ctx = canvas.getContext('2d')!;
    const imageData = ctx.createImageData(28, 28);
    
    // Extract and normalize the i-th feature map
    let min = Infinity;
    let max = -Infinity;
    for (let j = 0; j < 28 * 28; j++) {
      const val = conv1Data[i * 28 * 28 + j];
      min = Math.min(min, val);
      max = Math.max(max, val);
    }
    
    // Draw the normalized values
    for (let j = 0; j < 28 * 28; j++) {
      const val = conv1Data[i * 28 * 28 + j];
      const normalized = Math.floor(255 * (val - min) / (max - min));
      const idx = j * 4;
      imageData.data[idx] = normalized;     // R
      imageData.data[idx + 1] = normalized; // G
      imageData.data[idx + 2] = normalized; // B
      imageData.data[idx + 3] = 255;        // A
    }
    
    ctx.putImageData(imageData, 0, 0);
  }

  // Draw conv2 feature maps
  const conv2 = res["Plus112_output"];
  const conv2Data = conv2.data as Float32Array;
  for (let i = 0; i < 16; i++) {
    const canvas = document.getElementById(`conv2-${i}`) as HTMLCanvasElement;
    const ctx = canvas.getContext('2d')!;
    const imageData = ctx.createImageData(14, 14);
    
    // Extract and normalize the i-th feature map
    let min = Infinity;
    let max = -Infinity;
    for (let j = 0; j < 14 * 14; j++) {
      const val = conv2Data[i * 14 * 14 + j];
      min = Math.min(min, val);
      max = Math.max(max, val);
    }
    
    // Draw the normalized values
    for (let j = 0; j < 14 * 14; j++) {
      const val = conv2Data[i * 14 * 14 + j];
      const normalized = Math.floor(255 * (val - min) / (max - min));
      const idx = j * 4;
      imageData.data[idx] = normalized;     // R
      imageData.data[idx + 1] = normalized; // G
      imageData.data[idx + 2] = normalized; // B
      imageData.data[idx + 3] = 255;        // A
    }
    
    ctx.putImageData(imageData, 0, 0);
  }

  inferenceTime.value = time;
  sessionRunning.value = false;
};

const clear = () => {
  const ctx = (
    document.getElementById("input-canvas") as HTMLCanvasElement
  ).getContext("2d", { willReadFrequently: true }) as CanvasRenderingContext2D;
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  const ctxCenterCrop = (
    document.getElementById("input-canvas-centercrop") as HTMLCanvasElement
  ).getContext("2d", { willReadFrequently: true }) as CanvasRenderingContext2D;
  ctxCenterCrop.clearRect(
    0,
    0,
    ctxCenterCrop.canvas.width,
    ctxCenterCrop.canvas.height
  );
  const ctxScaled = (
    document.getElementById("input-canvas-scaled") as HTMLCanvasElement
  ).getContext("2d", { willReadFrequently: true }) as CanvasRenderingContext2D;
  ctxScaled.clearRect(0, 0, ctxScaled.canvas.width, ctxScaled.canvas.height);

  // Clear conv1 feature maps
  for (let i = 0; i < 8; i++) {
    const canvas = document.getElementById(`conv1-${i}`) as HTMLCanvasElement;
    const ctx = canvas.getContext('2d')!;
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  // Clear conv2 feature maps
  for (let i = 0; i < 16; i++) {
    const canvas = document.getElementById(`conv2-${i}`) as HTMLCanvasElement;
    const ctx = canvas.getContext('2d')!;
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  }

  output.value = new Float32Array(10);
  drawing.value = false;
  strokes.value = [];

  // Clear preprocessed input
  const preprocessedCanvas = document.getElementById("preprocessed-input") as HTMLCanvasElement;
  const preprocessedCtx = preprocessedCanvas.getContext('2d')!;
  preprocessedCtx.clearRect(0, 0, preprocessedCtx.canvas.width, preprocessedCtx.canvas.height);
};

const activateDraw = (e: any) => {
  if (modelLoadingError.value) {
    return;
  }
  drawing.value = true;
  strokes.value.push([]);
  const points = strokes.value[strokes.value.length - 1];
  points.push(mathUtils.getCoordinates(e));
  draw(e);
};

const draw = (e: any) => {
  if (!drawing.value) {
    return;
  }
  // disable scrolling behavior when drawing
  e.preventDefault();
  const ctx = (
    document.getElementById("input-canvas") as HTMLCanvasElement
  ).getContext("2d", { willReadFrequently: true }) as CanvasRenderingContext2D;
  ctx.lineWidth = 20;
  ctx.lineJoin = ctx.lineCap = "round";
  ctx.strokeStyle = "#393E46";
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  let points = strokes.value[strokes.value.length - 1];
  points.push(mathUtils.getCoordinates(e));
  // draw individual strokes
  for (let s = 0, slen = strokes.value.length; s < slen; s++) {
    points = strokes.value[s];
    let p1 = points[0];
    let p2 = points[1];
    ctx.beginPath();
    ctx.moveTo(p1[0], p1[1]);
    // draw points in stroke
    // quadratic bezier curve
    for (let i = 1, len = points.length; i < len; i++) {
      const midpoint = mathUtils.getMidpoint(p1, p2);
      ctx.quadraticCurveTo(p1[0], p1[1], midpoint[0], midpoint[1]);
      p1 = points[i];
      p2 = points[i + 1];
    }
    ctx.lineTo(p1[0], p1[1]);
    ctx.stroke();
  }
  
  run();
};

const stopDrawing = () => {
  drawing.value = false;
};

// Lifecycle hooks
onMounted(async () => {
  // fetch the model file to be used later
  const response = await fetch(props.modelFilepath);
  modelFile.value = await response.arrayBuffer();
  await initSession();
});
</script>

<style scoped lang="postcss">
@import "../../variables.css";
.image-panel {
  padding: 0;
  margin: 30px auto;
  background-color: white;
  min-height: 600px;
  width: fit-content;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0;

  & .loading-indicator {
    position: absolute;
    top: 5px;
    left: 5px;
  }

  & .error-message {
    color: var(--color-error);
    font-size: 12px;
    position: absolute;
    top: 5px;
    left: 5px;
  }
}
.input-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  margin-bottom: 20px;
}

.input-container {
  text-align: center;
  position: relative;
  user-select: none;
  
  & .input-label {
    font-family: var(--font-sans-serif);
    font-size: 18px;
    color: var(--color-lightgray);
    text-align: center;
    margin-bottom: 10px;
  }
  
  & .canvas-container {
    display: inline-flex;
    justify-content: center;
    border: 15px solid var(--color-blue-lighter);
    transition: border-color 0.2s ease-in;
    &:hover {
      border-color: var(--color-blue-light);
    }
    & canvas {
      width: 300px;
      height: 300px;
      background: whitesmoke;
      &:hover {
        cursor: crosshair;
      }
    }
  }
}

.preprocessed-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  
  & .layer-output {
    background: whitesmoke;
    padding: 15px;
    border-radius: 10px;
  }
}

.controls-column {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-monospace);
  padding-top: 80px;
  & .control {
    width: 100px;
    margin: 10px 0;
  }
}
.output-column {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  
  & .output {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    width: 200px;
    user-select: none;
    cursor: default;
    
    & .output-class {
      display: flex;
      flex-direction: row;
      align-items: center;
      margin: 5px 0;

      & .output-label {
        text-align: center;
        font-family: var(--font-sans-serif);
        font-size: 15px;
        color: black;
        padding: 0 6px;
        width: 25px;
      }

      & .output-bar {
        height: 16px;
        transition: width 0.2s ease-out;
        background: var(--color-blue-light);
      }

      &.predicted {
        .output-bar {
          background: var(--color-red);
        }
      }
    }
  }
}

.layer-outputs-container {
  position: relative;
  display: flex;
  justify-content: center;
  width: 100%;
  margin: 0;
  
  & .bg-line {
    position: absolute;
    z-index: 0;
    top: 0;
    left: 50%;
    background: whitesmoke;
    width: 15px;
    height: 100%;
  }
  & .layer-output {
    position: relative;
    z-index: 1;
    background: whitesmoke;
    border-radius: 10px;
    overflow-x: auto;
    padding: 10px;
    
    & .layer-output-heading {
      font-size: 1rem;
      color: #999999;
      margin-bottom: 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      font-size: 12px;
      & span.layer-class {
        color: var(--color-blue);
        font-size: 14px;
        font-weight: bold;
      }
    }
    & .layer-output-canvas-container {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      background: whitesmoke;
      & canvas {
        border: 1px solid lightgray;
        margin: 1px;
      }

      &.conv1-grid {
        display: grid;
        grid-template-columns: 84px;
        grid-template-rows: repeat(8, 84px);
        gap: 2px;
      }

      &.conv2-grid {
        display: grid;
        grid-template-columns: repeat(2, 84px);
        grid-template-rows: repeat(8, 84px);
        gap: 2px;
      }
    }
  }
}

.input-canvas {
  image-rendering: pixelated;
  width: 280px;
  height: 280px;
}
.conv1-canvas {
  image-rendering: pixelated;
  width: 84px;
  height: 84px;
}
.conv2-canvas {
  image-rendering: pixelated;
  width: 84px;
  height: 84px;
}

/* vue transition `fade` */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}


.panel-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  gap: 0;
}


</style>