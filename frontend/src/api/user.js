import request from "../utils/request";

export const loginAPI = (username, password) => {
  return request.post("/login", { username: username, password: password });
};
