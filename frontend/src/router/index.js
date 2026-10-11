import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/login.vue";
import AdminLayout from "../views/admin/AdminLayout.vue";
import StudentLayout from "../views/student/StudentLayout.vue";
import TeacherLayout from "../views/teacher/TeacherLayout.vue";

/** @type {import('vue-router').RouteRecordRaw[]} */

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
        component: () => import("../views/admin/QuestionManage.vue"),
      },
      {
        path: "student",
        component: () => import("../views/admin/StudentManage.vue"),
      },
      {
        path: "teacher",
        component: () => import("../views/admin/TeacherManage.vue"),
      },
      {
        path: "profile",
        component: () => import("../views/profile/UserProfile.vue"),
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
        component: () => import("../views/student/Lobby.vue"),
      },
      {
        path: "interview_room",
        component: () => import("../views/student/InterviewRoom.vue"),
      },
      {
        path: "history",
        component: () => import("../views/student/InterviewHistory.vue"),
      },
      {
        path: "profile",
        component: () => import("../views/profile/UserProfile.vue"),
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
        component: () => import("../views/teacher/ClassesManagement.vue"),
      },
      {
        path: "students",
        component: () => import("../views/teacher/StudentsManagement.vue"),
      },
      {
        path: "students/student_interview_history",
        component: () => import("../views/teacher/InterviewSHistory.vue"),
      },
      {
        path: "profile",
        component: () => import("../views/profile/UserProfile.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
});

// 路由守卫
router.beforeEach((to, from) => {
  const myToken = localStorage.getItem("token");

  if (to.path !== "/login" && !myToken) {
    return "/login";
  } else {
    return;
  }
});

export default router;
