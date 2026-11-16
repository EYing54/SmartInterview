<template>
  <div class="search-box">
    <el-input
      v-model="searchKeyword"
      :prefix-icon="Search"
      @focus="isFocused = true"
      @blur="isFocused = false"
    />
    <div v-show="!searchKeyword && !isFocused" class="search-placeholder">
      输入
      <span class="search-shortcut">/</span>
      以查询
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Search } from "@element-plus/icons-vue";

const searchKeyword = ref("");
const isFocused = ref(false);
</script>

<style scoped>
/* 搜索框 */
.search-box {
  position: relative;
  width: 250px;
}

.search-placeholder {
  position: absolute;
  left: 32px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  color: #a8abb2;
  font-size: 14px;
  pointer-events: none;
}

.search-shortcut {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 1px 5px;
  margin: 0 4px;
  font-size: 12px;
  background-color: #f4f4f5;
}
</style>
