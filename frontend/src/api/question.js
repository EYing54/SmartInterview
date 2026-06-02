import request from "../utils/request";

export const getQuestionList = (page, size) => {
  return request.post("/query_question", {
    page: page,
    size: size,
  });
};
