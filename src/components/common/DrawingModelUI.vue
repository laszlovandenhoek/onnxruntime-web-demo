<template>
  <div>
    <v-container fluid>
      <v-row
        justify="center"
        align="center"
        class="image-panel elevation-1"
      >
        <v-col cols="12" sm="6" md="4">
          <div class="input-column">
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
            </div>
            <v-row align="end" justify="end">
              <v-btn color="primary" @click="clear" style="margin: 0px">
                <v-icon icon="mdi-close" class="mr-2"></v-icon>
                Clear
              </v-btn>
            </v-row>
          </div>
        </v-col>

        <v-col cols="12" sm="6" md="4">
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
        </v-col>
      </v-row>
    </v-container>
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
const input = ref(new Float32Array(784));
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
  ).getContext("2d") as CanvasRenderingContext2D;
  const tensor = props.preprocess(ctx);
  const [res, time] = await runModelUtils.runModel(session.value!, tensor);
  output.value = props.postprocess(res);
  inferenceTime.value = time;
  sessionRunning.value = false;
};

const clear = () => {
  const ctx = (
    document.getElementById("input-canvas") as HTMLCanvasElement
  ).getContext("2d") as CanvasRenderingContext2D;
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  const ctxCenterCrop = (
    document.getElementById("input-canvas-centercrop") as HTMLCanvasElement
  ).getContext("2d") as CanvasRenderingContext2D;
  ctxCenterCrop.clearRect(
    0,
    0,
    ctxCenterCrop.canvas.width,
    ctxCenterCrop.canvas.height
  );
  const ctxScaled = (
    document.getElementById("input-canvas-scaled") as HTMLCanvasElement
  ).getContext("2d") as CanvasRenderingContext2D;
  ctxScaled.clearRect(0, 0, ctxScaled.canvas.width, ctxScaled.canvas.height);
  output.value = new Float32Array(10);
  drawing.value = false;
  strokes.value = [];
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
  ).getContext("2d") as CanvasRenderingContext2D;
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
  padding: 40px 20px;
  margin-top: 30px;
  background-color: white;
  position: relative;

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
.input-column {
  /* height: 100%; */
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  & .input-container {
    width: 100%;
    text-align: center;
    margin: 20px;
    position: relative;
    user-select: none;
    & .input-label {
      font-family: var(--font-sans-serif);
      font-size: 18px;
      color: var(--color-lightgray);
      text-align: center;
      & span.arrow {
        font-size: 36px;
        color: #cccccc;
        position: absolute;
        /* right: -32px; */
        top: 8px;
      }
    }
    & .canvas-container {
      display: inline-flex;
      justify-content: flex-end;
      margin: 10px 0;
      border: 15px solid var(--color-blue-lighter);
      transition: border-color 0.2s ease-in;
      &:hover {
        border-color: var(--color-blue-light);
      }
      & canvas {
        background: whitesmoke;
        &:hover {
          cursor: crosshair;
        }
      }
    }
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
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: left;
  margin-left: 80px;
  & .output {
    height: 300;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    user-select: none;
    cursor: default;
    & .output-class {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: center;
      padding: 10px 0;

      & .output-label {
        text-align: right;
        width: 35px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-family: var(--font-sans-serif);
        font-size: 15px;
        color: black;
        padding: 0 6px;
        border-right: 6px solid var(--color-blue-lighter);
      }

      & .output-bar {
        height: 16px;
        transition: width 0.2s ease-out;
        background: var(--color-blue-light);
      }

      & .output-value {
        text-align: left;
        margin-left: 20px;
        font-family: var(--font-sans-serif);
        font-size: 20px;
        color: black;
      }
    }
  }
}

.layer-outputs-container {
  position: relative;
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
    margin: 30px 20px;
    background: whitesmoke;
    border-radius: 10px;
    padding: 20px;
    overflow-x: auto;
    & .layer-output-heading {
      font-size: 1rem;
      color: #999999;
      margin-bottom: 10px;
      display: flex;
      flex-direction: column;
      font-size: 12px;
      & span.layer-class {
        color: var(--color-blue);
        font-size: 14px;
        font-weight: bold;
      }
    }
    & .layer-output-canvas-container {
      display: inline-flex;
      flex-wrap: wrap;
      background: whitesmoke;
      & canvas {
        border: 1px solid lightgray;
        margin: 1px;
      }
    }
  }
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
</style>