import { createRouter, createWebHashHistory } from 'vue-router'
import MNIST from '../components/models/MNIST.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL || '/'),
  routes: [
    {
      path: '/',
      name: 'home',
      component: MNIST,
    }
  ]
})

export default router
