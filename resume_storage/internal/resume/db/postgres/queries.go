package postgres

const (
	deleteResumeByIDQuery     = "delete from resume where resume_id = $1 and user_id = $2"
	getResumeInfoByIDQuery    = "select resume_id, user_id, created_at, title from resume where resume_id = $1 and user_id = $2"
	getAllResumesPreviewQuery = "select resume_id, user_id, created_at, title from resume where user_id = $1"
	createResumeQuery         = "insert into resume (user_id, title) values ($1, $2) returning resume_id"
)
