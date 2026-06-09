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

export const finishInterview = (interviewId) => {
  return request.post("/finish_interview", {
    interview_id: interviewId,
  });
};

export const abortInterview = (interviewId) => {
  return request.post("/abort_interview", {
    interview_id: interviewId,
  });
};

export const uploadAnswer = (formData) => {
  return request.post("/upload_answer", formData);
}; //特殊：用表单传输音视频文件数据
