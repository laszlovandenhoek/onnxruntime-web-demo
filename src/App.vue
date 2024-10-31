<template>
  <v-app>
    <v-main>
      <v-container
        fluid
        fill-height
        class="content-panel"
      >
        <div class="demo">
          <div class="ui-container">
            <router-view :hasWebGL="false"></router-view>
          </div>
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
// No setup needed - this is a simple container component
</script>

<style lang="postcss">
@import "./variables.css";

.application {
  font-family: var(--font-sans-serif) !important;
  font-size: 18px;
}

.application.theme--light {
  background: linear-gradient(0deg, #cccccc, #f0f0f0) !important;
  color: var(--color-darkgray);
}

footer {
  background: #cccccc !important;
}

.footer-label {
  font-family: var(--font-sans-serif);
  font-size: 16px;
  color: var(--color-lightgray);
  text-align: left;
  user-select: none;
  cursor: default;
}

a {
  text-decoration: none;
}

.demo {
  position: relative;
  width: 100%;
  height: 100%;
}

/*******************************************************************/
/* Vuetify overrides */

.navigation-drawer {
  background-color: whitesmoke !important;
}

.input-group--select .input-group__selections__comma,
.input-group input,
.input-group textarea {
  font-size: 20px !important;
  color: var(--color-black) !important;
}

.input-group:not(.input-group--error) label {
  font-size: 20px !important;
  color: var(--color-lightgray) !important;
}

.list .list__tile:not(.list__tile--active) {
  color: var(--color-darkgray) !important;
}

.list__tile {
  font-size: 16px !important;
  height: 35px !important;
  font-family: var(--font-monospace);
}

.content-panel {
  padding: 0 !important;
}

.select-backend {
  text-align: center;
  font-family: var(--font-sans-serif);
  font-size: 20px;
  color: var(--color-black);
  margin-right: 10px;
}

.error-message {
  color: var(--color-error);
  font-size: 15px;
  text-align: center;
}
</style>
