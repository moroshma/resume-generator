box.cfg {
    listen = '0.0.0.0:3301',
    log_level = 5  -- Устанавливаем максимальный уровень логирования
}

require('log').info("I am a test app!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
local utils = require('utils.utils')

-- Создаем спейс для пользователей если он не существует
local function create_spaces()
    local users = box.schema.space.create('users', {
        if_not_exists = true,
    })

    -- Определяем формат после создания спейса
    users:format({
        { name = 'id', type = 'unsigned' },
        { name = 'login', type = 'string' },
        { name = 'password', type = 'string' }
    })

    -- Создаем индексы
    users:create_index('primary', {
        type = 'hash',
        parts = { 'id' },
        if_not_exists = true
    })

    users:create_index('login', {
        type = 'hash',
        parts = { 'login' },
        if_not_exists = true,
        unique = true
    })
end

-- Создаем пользователя для внешних подключений
local function create_user()
    box.schema.user.create('user_service', {
        password = 'gopassword',
        if_not_exists = true
    })

    -- Даем права пользователю
    box.schema.user.grant('user_service', 'read,write,execute', 'universe', nil, { if_not_exists = true })
end

-- Функция для создания нового пользователя в спейсе

function create_new_user(login, password)
    if type(login) ~= 'string' or type(password) ~= 'string' then
        return utils.raw_response({ error = "Login and password must be strings" })
    end

    local users = box.space.users
    local exists = users.index.login:get(login)
    if exists ~= nil then
        return utils.raw_response({ error = "User with this login already exists" })
    end

    local max_id = 0
    for _, tuple in users:pairs() do
        if tuple[1] > max_id then
            max_id = tuple[1]
        end
    end

    local new_id = max_id + 1
    users:insert({ new_id, login, password })
    require('log').info("add new user " .. tostring(new_id))

    return utils.raw_response({id = new_id})
end

function get_user_by_login(login)
    if type(login) ~= 'string' then
        return utils.raw_response({ error = "Login and password must be strings" })
    end

    local users = box.space.users
    local user = users.index.login:get(login)
    if user == nil then
        return utils.raw_response({ error = "User not found" })
    end
    
    return utils.raw_response({ id = user[1], login = user[2], password = user[3] })
end

-- Вызываем функции инициализации
box.once('init', function()
    create_spaces()
    create_user()
end)

-- В конце файла
require('log').info("Initialization completed!")
