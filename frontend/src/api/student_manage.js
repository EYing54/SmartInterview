import request from "../utils/request";

export const getStudentList = (page, size) => {
  return request.post("/get_student_list", {
    page: page,
    size: size,
  });
};

export const deleteAccount = (userIds) => {
  return request.post("/delete_s_account", { user_ids: userIds });
}; //user_id的数据类型是数组

export const resetAccount = (userId) => {
  return request.post("/reset_s_account_password", { user_id: userId });
}; //user_id的数据类型也是数组
