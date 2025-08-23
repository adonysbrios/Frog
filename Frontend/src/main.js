import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import { ViewTransitionsPlugin } from 'vue-view-transitions'

const app = createApp(App)

app.use(router)
app.use(ViewTransitionsPlugin())

app.mount('#app')
