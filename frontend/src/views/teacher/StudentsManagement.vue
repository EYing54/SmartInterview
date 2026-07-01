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
        班级简介：{{ currentClassIntroduce }}
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

    <el-button
      type="primary"
      plain
      :icon="Plus"
      style="
        width: 100%;
        margin-bottom: 15px;
        border-style: dashed;
        border-width: 2px;
      "
      @click="dialogVisible = true"
      >添加学生</el-button
    >

    <el-dialog
      v-model="dialogVisible"
      title="导入学生名单"
      width="500px"
      @closed="handleRemove"
    >
      <el-upload
        v-if="!selectedFile"
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        accept=".xlsx, .xls"
        :limit="1"
        :show-file-list="false"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽 Excel 文件到此处，或点击选择文件</div>
      </el-upload>

      <div
        v-else
        style="
          text-align: center;
          padding: 40px 0;
          border: 1px dashed #d9d9d9;
          border-radius: 6px;
        "
      >
        <el-icon style="font-size: 48px; color: #67c23a; margin-bottom: 10px"
          ><DocumentChecked
        /></el-icon>
        <div style="font-size: 14px; color: #606266; margin-bottom: 20px">
          已选择文件：{{ selectedFile.name }}
        </div>
        <el-button type="danger" plain @click="handleRemove" size="small"
          >重新选择</el-button
        >
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="submitUpload">导入</el-button>
          <el-button type="danger" @click="dialogVisible = false"
            >取消</el-button
          >
        </span>
      </template>
    </el-dialog>

    <el-empty v-if="studentList.length === 0" description="该班级暂无学生" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import {
  queryStudents,
  importStudents,
  removeStudent,
} from "../../api/classes";
import {
  Delete,
  Plus,
  UploadFilled,
  DocumentChecked,
} from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const currentClassName = ref("");
const currentClassIntroduce = ref("");
const route = useRoute();
const currentClassId = ref("");
const studentList = ref([]);
const dialogVisible = ref(false);
const selectedFile = ref(null);

currentClassId.value = route.query.id;

const getClassStudents = async () => {
  try {
    const res = await queryStudents(currentClassId.value);
    studentList.value = res.data.data?.student_list || [];
    currentClassName.value = res.data.data?.class_name || "未知班级";
    currentClassIntroduce.value =
      res.data.data?.class_introduce || "这里什么都木有0A0 ! ";
  } catch (error) {
    console.log(error);
  }
};

const removeCurrentStudent = (id) => {
  ElMessageBox.confirm("确定要将该学生移出班级吗？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        await removeStudent(id);
        ElMessage.success("删除成功！");
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

const handleFileChange = (uploadFile) => {
  selectedFile.value = uploadFile.raw;
};

const handleExceed = () => {
  ElMessage.warning("只能选择一个文件，请先移除当前文件后再重新选择。");
};

const handleRemove = () => {
  selectedFile.value = null;
};

const submitUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning("请先选择一个 Excel 文件！");
    return;
  }
  try {
    const res = await importStudents(currentClassId.value, selectedFile.value);
    ElMessage.success(res.data.msg);
    dialogVisible.value = false;
    selectedFile.value = null;
    getClassStudents();
  } catch (error) {
    console.log(error);
    const errorMsg =
      error.response?.data?.msg || "导入失败，请检查文件格式或稍后重试";
    ElMessage.error(errorMsg);
  }
};

onMounted(() => {
  getClassStudents();
});
</script>
