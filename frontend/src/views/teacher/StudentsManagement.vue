<template>
  <div style="padding: 20px; max-width: 1000px; margin: 0 auto">
    <div
      style="
        margin-bottom: 25px;
        border-left: 5px solid #409eff;
        padding-left: 15px;
      "
    >
      <h2 style="margin: 0 0 8px 0">{{ currentClassName }}</h2>
      <div style="color: #666; font-size: 14px">
        {{ currentClassIntroduce }}
      </div>
    </div>

    <el-card
      v-for="student in studentList"
      :key="student.student_id"
      shadow="hover"
      style="margin-bottom: 12px"
    >
      <div
        style="
          display: flex;
          justify-content: space-between;
          align-items: center;
        "
      >
        <div style="font-size: 16px; font-weight: bold">
          {{ student.student_name }}
        </div>

        <div>
          <el-button
            @click.stop="checkInterview(student.student_id)"
            type="success"
            plain
            >查看面试</el-button
          >
          <el-button @click.stop="checkResume" type="primary" plain
            >查看简历</el-button
          >
          <el-button
            @click="removeCurrentStudent(student.student_id)"
            type="danger"
            plain
            :icon="Delete"
            >删除</el-button
          >
        </div>
      </div>
    </el-card>

    <el-empty v-if="studentList.length === 0" description="该班级暂无学生" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { queryStudents } from "../../api/classes";
import { Delete } from "@element-plus/icons-vue";
import { removeStudent } from "../../api/classes";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const currentClassName = ref("");
const currentClassIntroduce = ref("");
const route = useRoute();
const currentClassId = ref("");
const studentList = ref([]);

currentClassId.value = route.query.id;
const getClassStudents = async () => {
  try {
    const res = await queryStudents(currentClassId.value);
    studentList.value = res.data.data?.student_list || [];
    currentClassName.value = res.data.data?.class_name || "未知班级";
    currentClassIntroduce.value = res.data.data?.class_introduce || "暂无简介";
    console.log("收到的数据为：", res.data.data);
  } catch (error) {
    console.log(error);
  }
};

const removeCurrentStudent = (id) => {
  // 二次确认弹窗
  ElMessageBox.confirm("确定要将该学生移出班级吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        const res = await removeStudent(id);
        ElMessage.success("删除成功！");
        // 静默刷新页面！
        getClassStudents();
      } catch (error) {
        console.log(error);
        ElMessage.error("删除失败，请重试");
      }
    })
    .catch(() => {});
};

const checkInterview = (studentId) => {
  router.push({
    path: "/teacher/students/student_interview_history",
    query: { id: studentId },
  });
};

const checkResume = (interviewId) => {
  console.log("");
};

onMounted(() => {
  getClassStudents();
});
</script>
