package usecase

import "fmt"

func generateResumeObjectName(userID, resumeID uint) string {
	return fmt.Sprintf("user-%d-resume-%d.pdf", userID, resumeID)
}
