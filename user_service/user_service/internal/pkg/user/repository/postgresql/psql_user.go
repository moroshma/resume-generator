package postgresql

import (
	"context"
	"encoding/json"
	"errors"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/moroshma/resume-generator/user_service/internal/pkg/models"
)

type psqlUserRepository struct {
	db *pgxpool.Pool
}

func NewPsqlUserRepository(db *pgxpool.Pool) models.UserRepositoryI {
	return &psqlUserRepository{db}
}

func (pgRepo *psqlUserRepository) Create(user models.User) (uint, error) {
	roleIDs := make([]uint, len(user.Roles))
	for i, role := range user.Roles {
		roleIDs[i] = role.ID
	}

	var insertedID uint
	err := pgRepo.db.QueryRow(context.Background(), "SELECT insert_user_with_roles($1, $2, $3)",
		user.Login, user.Password, roleIDs).Scan(&insertedID)
	return insertedID, err
}

func (pgRepo *psqlUserRepository) Get(id uint) (json.RawMessage, error) {
	var userJSON json.RawMessage
	err := pgRepo.db.QueryRow(context.Background(), "SELECT get_user_by_id($1)", id).Scan(&userJSON)
	return userJSON, err
}

func (pgRepo *psqlUserRepository) GetAll() (json.RawMessage, error) {
	var usersJSON json.RawMessage
	err := pgRepo.db.QueryRow(context.Background(), "SELECT get_all_users()").Scan(&usersJSON)
	return usersJSON, err
}

func (pgRepo *psqlUserRepository) Update(user models.User) error {
	roleIDs := make([]uint, len(user.Roles))
	for i, role := range user.Roles {
		roleIDs[i] = role.ID
	}

	var rowsAffected uint
	err := pgRepo.db.QueryRow(context.Background(), "SELECT update_user_with_roles($1, $2, $3, $4)", user.ID, user.Login,
		user.Password, roleIDs).Scan(&rowsAffected)
	if err != nil {
		return err
	}

	if rowsAffected == 0 {
		return errors.New("Can't update enexisting row")
	}

	return nil
}

func (pgRepo *psqlUserRepository) Delete(id uint) error {
	var rowsAffected uint
	err := pgRepo.db.QueryRow(context.Background(), "SELECT delete_user($1)", id).Scan(&rowsAffected)
	if err != nil {
		return err
	}

	if rowsAffected != 1 {
		return errors.New("Can't delete enexisting row")
	}

	return nil
}

func (pgRepo *psqlUserRepository) GetUserByLogin(login string) (models.User, error) {
	user := models.User{Login: login}
	err := pgRepo.db.QueryRow(context.Background(), "SELECT id, password FROM users WHERE login=$1", login).Scan(&user.ID, &user.Password)
	return user, err
}
