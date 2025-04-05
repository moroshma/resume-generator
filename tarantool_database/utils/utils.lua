local json = require('json')

local function make_response(elem)
    if elem == nil then
        return {
            status = 204
        }
    end
    return {
        status = 200,
        headers = { ['Content-Type'] = 'application/json' },
        body = json.encode({ data = elem })
    }
end

local function make_raw_response(elem)
    if elem == nil then
        return {
            status = 204
        }
    end

    return {
        status = 200,
        headers = { ['Content-Type'] = 'application/json' },
        body = json.encode(elem)
    }
end

return {
    response = make_response,
    raw_response = make_raw_response
}