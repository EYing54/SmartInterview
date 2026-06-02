import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/login.vue";
import Home from "../views/home.vue";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    component: Login,
  },
  {
    path: "/home",
    component: Home,
  },
];
const router = createRouter({
  history: createWebHistory(),
  routes: routes,
});

export default router;
