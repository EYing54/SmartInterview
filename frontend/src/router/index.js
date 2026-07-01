import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/login.vue";
import QuestionManage from "../views/admin/QuestionManage.vue";
import AdminLayout from "../views/admin/AdminLayout.vue";
import StudentLayout from "../views/student/StudentLayout.vue";
import Lobby from "../views/student/Lobby.vue";
import { patchProp } from "vue";
import InterviewRoom from "../views/student/InterviewRoom.vue";
import TeacherLayout from "../views/teacher/TeacherLayout.vue";
import ClassesManagement from "../views/teacher/ClassesManagement.vue";
import StudentsManagement from "../views/teacher/StudentsManagement.vue";
import InterviewSHistory from "../views/teacher/InterviewSHistory.vue";

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
    redirect: "/admin/question",
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
  {
    path: "/teacher",
    component: TeacherLayout,
    redirect: "/teacher/classes",
    children: [
      {
        path: "classes",
        component: ClassesManagement,
      },
      {
        path: "students",
        component: StudentsManagement,
      },
      {
        path: "students/student_interview_history",
        component: InterviewSHistory,
      },
    ],
  },
];
const router = createRouter({
  history: createWebHistory(),
  routes: routes,
});

//路由守卫
router.beforeEach((to, from, next) => {
  const myToken = localStorage.getItem("token");
  if (to.path !== "/login" && !myToken) {
    next("/login");
  } else {
    next();
  }
});

export default router;
