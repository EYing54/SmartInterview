import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/login.vue";
import QuestionManage from "../views/admin/QuestionManage.vue";
import AdminLayout from "../views/admin/AdminLayout.vue";
import StudentLayout from "../views/student/StudentLayout.vue";
import Lobby from "../views/student/Lobby.vue";
import { patchProp } from "vue";
import InterviewRoom from "../views/student/InterviewRoom.vue";

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
    path: "/admin",
    component: AdminLayout,
    redirectL: "/admin/question",
    children: [
      {
        path: "question",
        component: QuestionManage,
      },
    ],
  },
  {
    path: "/student",
    component: StudentLayout,
    redirect: "/student/lobby",
    children: [
      {
        path: "lobby",
        component: Lobby,
      },
      {
        path: "interview_room",
        component: InterviewRoom,
      },
      {
        path: "history",
        component: () => import("../views/student/InterviewHistory.vue"),
      },
    ],
  },
];
const router = createRouter({
  history: createWebHistory(),
  routes: routes,
});

export default router;
