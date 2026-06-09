from datetime import datetime, timedelta
from extensions import db, scheduler
from app.models.record import InterviewRecord


@scheduler.task("interval", id="clean_dirty_interview", minutes=45)
def clean_dirty_interview():
    with scheduler.app.app_context():
        one_hour_ago = datetime.now() - timedelta(hours=1)

        deleted_count = InterviewRecord.query.filter(
            InterviewRecord.status == 0, InterviewRecord.create_time < one_hour_ago
        ).delete(synchronize_session=False)

        db.session.commit()
        print(f"[{datetime.now()}] 清理了{deleted_count}条数据！")
