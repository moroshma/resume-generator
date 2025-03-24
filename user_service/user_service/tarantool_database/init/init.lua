box.cfg {
    listen = '0.0.0.0:3301',
    log_level = 5  -- Устанавливаем максимальный уровень логирования
}

require('log').info("I am a test app!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
local utils = require('utils.utils')
local json = require('json')

-- Создаем спейсы для хранения данных
local function create_spaces()
    -- Основной спейс пользователей (оставляем существующий)
    local users = box.schema.space.create('users', {
        if_not_exists = true,
    })
    users:format({
        { name = 'id', type = 'unsigned' },
        { name = 'login', type = 'string' },
        { name = 'password', type = 'string' }
    })
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

    -- Спейс для информации о пользователе
    local user_info = box.schema.space.create('user_info', {
        if_not_exists = true,
    })
    user_info:format({
        { name = 'user_id', type = 'unsigned' },
        { name = 'name', type = 'string' },
        { name = 'surname', type = 'string' },
        { name = 'email', type = 'string', is_nullable = true },
        { name = 'github', type = 'string', is_nullable = true },
        { name = 'phone_number', type = 'string', is_nullable = true },
        { name = 'location', type = 'string', is_nullable = true },
        { name = 'linkedin', type = 'string', is_nullable = true },
        { name = 'telegram', type = 'string', is_nullable = true }
    })
    user_info:create_index('primary', {
        type = 'hash',
        parts = { 'user_id' },
        if_not_exists = true,
        unique = true
    })

    -- Спейс для образования
    local education = box.schema.space.create('education', {
        if_not_exists = true,
    })
    education:format({
        { name = 'id', type = 'unsigned' },
        { name = 'user_id', type = 'unsigned' },
        { name = 'institution', type = 'string' },
        { name = 'degree', type = 'string' },
        { name = 'from_date', type = 'string' },
        { name = 'to_date', type = 'string', is_nullable = true }
    })
    education:create_index('primary', {
        type = 'hash',
        parts = { 'id' },
        if_not_exists = true
    })
    education:create_index('user_id', {
        type = 'tree',
        parts = { 'user_id' },
        unique = false,
        if_not_exists = true
    })

    -- Спейс для опыта работы
    local experience = box.schema.space.create('experience', {
        if_not_exists = true,
    })
    experience:format({
        { name = 'id', type = 'unsigned' },
        { name = 'user_id', type = 'unsigned' },
        { name = 'company', type = 'string' },
        { name = 'role', type = 'string' },
        { name = 'from_date', type = 'string' },
        { name = 'to_date', type = 'string', is_nullable = true },
        { name = 'description', type = 'string', is_nullable = true }
    })
    experience:create_index('primary', {
        type = 'hash',
        parts = { 'id' },
        if_not_exists = true
    })
    experience:create_index('user_id', {
        type = 'tree',
        parts = { 'user_id' },
        unique = false,
        if_not_exists = true
    })

    -- Спейс для языков
    local languages = box.schema.space.create('languages', {
        if_not_exists = true,
    })
    languages:format({
        { name = 'id', type = 'unsigned' },
        { name = 'user_id', type = 'unsigned' },
        { name = 'language', type = 'string' }
    })
    languages:create_index('primary', {
        type = 'hash',
        parts = { 'id' },
        if_not_exists = true
    })
    languages:create_index('user_id', {
        type = 'tree',
        parts = { 'user_id' },
        unique = false,
        if_not_exists = true
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

-- Вспомогательная функция для генерации ID
local function get_next_id(space_name)
    local space = box.space[space_name]
    local max_id = 0
    for _, tuple in space:pairs() do
        if tuple[1] > max_id then
            max_id = tuple[1]
        end
    end
    return max_id + 1
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

    local new_id = get_next_id('users')
    users:insert({ new_id, login, password })
    require('log').info("add new user " .. tostring(new_id))

    return utils.raw_response({
        status = 200,

        id = new_id,
        login = login

    })
end

-- Функция для создания или обновления информации о пользователе
function create_user_info(info)
    if type(info) ~= 'string' then
        return utils.raw_response({ error = "Info must be a JSON string" })
    end

    local data = json.decode(info)
    if not data then
        return utils.raw_response({ error = "Invalid JSON format" })
    end

    if not data.name or not data.surname then
        return utils.raw_response({ error = "Name and surname are required" })
    end

    -- Генерируем новый ID пользователя если он не предоставлен
    local user_id = data.user_id or get_next_id('user_info')

    -- Создаем основную информацию
    box.space.user_info:insert({
        user_id,
        data.name,
        data.surname,
        data.email or '',
        data.github or '',
        data.phone_number or '',
        data.location or '',
        (data.social_profiles and data.social_profiles.linkedin) or '',
        (data.social_profiles and data.social_profiles.telegram) or ''
    })

    -- Добавляем образование
    if data.education then
        for _, edu in ipairs(data.education) do
            if not edu.institution or not edu.degree or not edu.from then
                return utils.raw_response({ error = "Institution, degree and from date are required for education" })
            end
            box.space.education:insert({
                get_next_id('education'),
                user_id,
                edu.institution,
                edu.degree,
                edu.from,
                edu.to or ''
            })
        end
    end

    -- Добавляем опыт работы
    if data.experience then
        for _, exp in ipairs(data.experience) do
            if not exp.company or not exp.role or not exp.from then
                return utils.raw_response({ error = "Company, role and from date are required for experience" })
            end
            box.space.experience:insert({
                get_next_id('experience'),
                user_id,
                exp.company,
                exp.role,
                exp.from,
                exp.to or '',
                exp.description or ''
            })
        end
    end

    -- Добавляем языки
    if data.languages then
        for _, lang in ipairs(data.languages) do
            box.space.languages:insert({
                get_next_id('languages'),
                user_id,
                lang
            })
        end
    end

    return utils.raw_response({
        status = 200,
        body = json.encode({
            id = user_id,
            name = data.name,
            surname = data.surname
        })
    })
end

-- Функция для получения информации о пользователе
function get_user_info(user_id)
    if type(user_id) ~= 'number' then
        return utils.raw_response({ error = "User ID must be a number" })
    end

    local info = box.space.user_info:get(user_id)
    if not info then
        return utils.raw_response({ error = "User info not found" })
    end

    local result = {
        user_id = info[1],
        name = info[2],
        surname = info[3],
        email = info[4],
        github = info[5],
        phone_number = info[6],
        location = info[7],
        social_profiles = {
            linkedin = info[8],
            telegram = info[9]
        },
        education = {},
        experience = {},
        languages = {}
    }

    -- Получаем образование
    for _, edu in box.space.education.index.user_id:pairs(user_id) do
        table.insert(result.education, {
            institution = edu[3],
            degree = edu[4],
            from = edu[5],
            to = edu[6]
        })
    end

    -- Получаем опыт работы
    for _, exp in box.space.experience.index.user_id:pairs(user_id) do
        table.insert(result.experience, {
            company = exp[3],
            role = exp[4],
            from = exp[5],
            to = exp[6],
            description = exp[7]
        })
    end

    -- Получаем языки
    for _, lang in box.space.languages.index.user_id:pairs(user_id) do
        table.insert(result.languages, lang[3])
    end

    return utils.raw_response(
            result
    )
end

-- Функция для получения пользователя по логину
function get_user_by_login(login)
    if type(login) ~= 'string' then
        return utils.raw_response({ error = "Login must be a string" })
    end

    local users = box.space.users
    local user = users.index.login:get(login)
    if user == nil then
        return utils.raw_response({ error = "User not found" })
    end

    return utils.raw_response({
        status = 200,
        id = user[1],
        login = user[2],
        password = user[3]
    })

end

-- Вызываем функции инициализации
box.once('init', function()
    create_spaces()
    create_user()
end)

-- В конце файла
require('log').info("Initialization completed!")
