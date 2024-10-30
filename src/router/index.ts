import Vue from 'vue';
import Router from 'vue-router';

import MNIST from '../components/models/MNIST.vue';

Vue.use(Router);

export default new Router({
  mode: 'hash',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '*',
      name: 'home',
      component: MNIST,
    }
  ],
});
