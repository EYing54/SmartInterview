import request from "../utils/request";

export const createInterview = () => {
  return request.post("/create_interview");
};

export const getHistoryList = () => {
  return request.get("/get_interview_history");
};

export const getInterviewDetail = (id) => {
  return request.get(`/get_interview_detail?interview_id=${id}`);
};
