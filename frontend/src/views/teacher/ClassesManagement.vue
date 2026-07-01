<template>
  <div style="padding: 20px; max-width: 1000px; margin: 0 auto">
    <div
      style="
        margin-bottom: 25px;
        border-left: 5px solid #409eff;
        padding-left: 15px;
      "
    >
      <h2 style="margin-bottom: 20px">我的班级</h2>
    </div>

    <el-card
      v-for="item in classList"
      :key="item.class_id"
      shadow="hover"
      style="margin-bottom: 15px; cursor: pointer"
      @click="goToStudents(item.class_id)"
    >
      <div
        style="
          display: flex;
          justify-content: space-between;
          align-items: center;
        "
      >
        <div>
          <div style="font-size: 18px; font-weight: bold; color: #303133">
            {{ item.class_name }}
          </div>
          <div style="font-size: 13px; color: #909399; margin-top: 6px">
            班级简介：{{ item.class_introduce || "这里什么都木有0A0 !" }}
          </div>
        </div>

        <div>
          <el-button
            type="primary"
            plain
            :icon="Edit"
            @click.stop="editClassInformation(item)"
            >编辑</el-button
          >

          <el-button
            type="danger"
            plain
            :icon="Delete"
            @click.stop="deleteCurrentClass(item.class_id)"
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
      @click="createNewClass"
      >新增班级
    </el-button>

    <el-empty
      v-if="classList.length === 0"
      description="您目前还没有管理的班级"
    />
  </div>

  <el-dialog
    v-model="dialogVisible"
    :title="dialogType === 'create' ? '创建班级' : '编辑班级'"
    width="500px"
  >
    <el-form :model="classForm" label-width="80px">
      <el-form-item label="班级名称">
        <el-input
          v-model="classForm.className"
          maxlength="20"
          show-word-limit
          placeholder="请输入班级名称"
        ></el-input>
      </el-form-item>

      <el-form-item label="班级简介">
        <el-input
          v-model="classForm.classIntroduce"
          type="textarea"
          maxlength="50"
          show-word-limit
          placeholder="请输入班级简介"
        ></el-input>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="submitForm" type="primary">确认</el-button>
      <el-button @click="dialogVisible = false" type="danger">取消</el-button>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref, onMounted } from "vue";
import {
  queryMyClasses,
  deleteClass,
  createClass,
  updateClassInformation,
} from "../../api/classes";
import { useRouter } from "vue-router";
import { Delete, Edit, Plus } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";

const classList = ref([]);
const getMyClasses = async () => {
  try {
    const res = await queryMyClasses();
    classList.value = res.data.data || [];
    console.log("收到的班级数据为：", res.data.data);
  } catch (error) {
    console.log(error);
  }
};

//点击卡片跳转至学生列表页
const router = useRouter();
const goToStudents = (classId) => {
  router.push({
    path: "/teacher/students",
    query: { id: classId },
  });
};

const deleteCurrentClass = (id) => {
  ElMessageBox.confirm("确定要删除该班级吗？", "警告", {
    cancelButtonText: "取消",
    confirmButtonText: "确认",
    type: "warning",
  })
    .then(async () => {
      try {
        const res = await deleteClass(id);
        ElMessage.success("删除成功！");
        getMyClasses();
      } catch (error) {
        console.log(error);
        ElMessage.error("删除失败！");
      }
    })
    .catch(() => {});
};

const classForm = ref({ classId: null, className: "", classIntroduce: "" });
const dialogVisible = ref(false);
const dialogType = ref("create");
//点击了"创建班级"按钮会执行的
const createNewClass = () => {
  dialogType.value = "create";
  dialogVisible.value = true;
  classForm.value = { classId: null, className: "", classIntroduce: "" };
};
//点击了“编辑”按钮会执行的
const editClassInformation = (item) => {
  dialogType.value = "edit";
  dialogVisible.value = true;
  classForm.value = {
    classId: item.class_id,
    className: item.class_name,
    classIntroduce: item.class_introduce || "",
  };
};
//完成最后的提交
const submitForm = async () => {
  try {
    if (dialogType.value === "create") {
      const res = await createClass(
        classForm.value.className,
        classForm.value.classIntroduce,
      );
      ElMessage.success("创建成功！");
    }
    if (dialogType.value === "edit") {
      const res = await updateClassInformation(
        classForm.value.classId,
        classForm.value.className,
        classForm.value.classIntroduce,
      );
      ElMessage.success("修改成功！");
    }
    dialogVisible.value = false;
    getMyClasses();
  } catch (error) {
    console.log(error);
    ElMessage.error("操作失败！");
  }
};

onMounted(() => {
  getMyClasses();
});
</script>
