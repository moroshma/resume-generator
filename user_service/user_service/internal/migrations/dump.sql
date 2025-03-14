--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3 (Ubuntu 16.3-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: delete_role(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_role(role_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    rows_affected INTEGER;
BEGIN
    -- Delete the role with the specified id
    DELETE FROM roles
    WHERE id = role_id;

    -- Get the number of rows affected
    GET DIAGNOSTICS rows_affected = ROW_COUNT;

    -- Return the number of rows affected
    RETURN rows_affected;
END;
$$;


ALTER FUNCTION public.delete_role(role_id integer) OWNER TO postgres;

--
-- Name: delete_user(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_user(user_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    rows_affected INTEGER;
BEGIN
    -- Delete the user with the specified id
    DELETE FROM users
    WHERE id = user_id;

    -- Get the number of rows affected
    GET DIAGNOSTICS rows_affected = ROW_COUNT;

    -- Return the number of rows affected
    RETURN rows_affected;
END;
$$;


ALTER FUNCTION public.delete_user(user_id integer) OWNER TO postgres;

--
-- Name: get_all_roles(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_all_roles() RETURNS json
    LANGUAGE plpgsql
    AS $$
DECLARE
    roles_json JSON;
BEGIN
    -- Fetch all roles and convert to JSON
    SELECT json_agg(row_to_json(r))
    INTO roles_json
    FROM (
        SELECT id, name
        FROM roles
    ) r;

    -- Return the JSON array of roles
    RETURN roles_json;
END;
$$;


ALTER FUNCTION public.get_all_roles() OWNER TO postgres;

--
-- Name: get_all_users(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_all_users() RETURNS json
    LANGUAGE plpgsql
    AS $$
DECLARE
    users_json JSON;
BEGIN
    -- Fetch all users with their roles
    SELECT json_agg(row_to_json(u))
    INTO users_json
    FROM (
        SELECT u.id, u.login,
               (SELECT json_agg(row_to_json(r))
                FROM roles r
                JOIN users_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = u.id
               ) AS roles
        FROM users u
    ) u;

    -- Return the JSON array of users
    RETURN users_json;
END;
$$;


ALTER FUNCTION public.get_all_users() OWNER TO postgres;

--
-- Name: get_role_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_role_by_id(role_id integer) RETURNS json
    LANGUAGE plpgsql
    AS $$
DECLARE
    role_json JSON;
BEGIN
    -- Fetch the role with the specified id
    SELECT row_to_json(r)
    INTO role_json
    FROM (
        SELECT id, name
        FROM roles
        WHERE id = role_id
    ) r;

    -- Return the JSON object
    RETURN role_json;
END;
$$;


ALTER FUNCTION public.get_role_by_id(role_id integer) OWNER TO postgres;

--
-- Name: get_roles_by_user_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_roles_by_user_id(id_user integer) RETURNS json
    LANGUAGE plpgsql
    AS $$
DECLARE
    roles_json JSON;
BEGIN
    -- Retrieve role names as JSON array
    SELECT json_agg(r.name ORDER BY r.id)
    INTO roles_json
    FROM roles r
    JOIN users_roles ur ON r.id = ur.role_id
    WHERE ur.user_id = id_user;

    -- Return the JSON array of role names
    RETURN roles_json;
END;
$$;


ALTER FUNCTION public.get_roles_by_user_id(id_user integer) OWNER TO postgres;

--
-- Name: get_user_by_id(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_user_by_id(id_user integer) RETURNS json
    LANGUAGE plpgsql
    AS $$
DECLARE
    user_json JSON;
BEGIN
    -- Fetch the user with the specified id and their roles
    SELECT row_to_json(u)
    INTO user_json
    FROM (
        SELECT u.id, u.login,
               (SELECT json_agg(row_to_json(r))
                FROM roles r
                JOIN users_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = u.id
               ) AS roles
        FROM users u
        WHERE u.id = id_user
    ) u;

    -- Return the JSON object
    RETURN user_json;
END;
$$;


ALTER FUNCTION public.get_user_by_id(id_user integer) OWNER TO postgres;

--
-- Name: insert_role(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.insert_role(role_name character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    new_role_id INTEGER;
BEGIN
    -- Insert the new role and get the generated id
    INSERT INTO roles(name) VALUES (role_name) RETURNING id INTO new_role_id;

    -- Return the new role id
    RETURN new_role_id;
END;
$$;


ALTER FUNCTION public.insert_role(role_name character varying) OWNER TO postgres;

--
-- Name: insert_user_with_roles(character varying, character varying, integer[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.insert_user_with_roles(user_login character varying, user_password character varying, role_ids integer[]) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    new_user_id INTEGER;
    role_id INT;
BEGIN
    -- Insert the user into the users table and get the new user ID
    INSERT INTO users (login, password) 
    VALUES (user_login, user_password)
    RETURNING id INTO new_user_id;

    -- Loop through the role IDs array and link each role to the user
    FOR role_id IN SELECT UNNEST(role_ids)
    LOOP
        -- Insert the user-role relationship
        INSERT INTO users_roles (user_id, role_id)
        VALUES (new_user_id, role_id);
    END LOOP;

    -- Return the new user ID
    RETURN new_user_id;
END;
$$;


ALTER FUNCTION public.insert_user_with_roles(user_login character varying, user_password character varying, role_ids integer[]) OWNER TO postgres;

--
-- Name: update_role(integer, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_role(role_id integer, new_name character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    rows_affected INTEGER;
BEGIN
    -- Update the role with the specified id
    UPDATE roles
    SET name = new_name
    WHERE id = role_id;

    -- Get the number of rows affected
    GET DIAGNOSTICS rows_affected = ROW_COUNT;

    -- Return the number of rows affected
    RETURN rows_affected;
END;
$$;


ALTER FUNCTION public.update_role(role_id integer, new_name character varying) OWNER TO postgres;

--
-- Name: update_user_with_roles(integer, character varying, character varying, integer[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_user_with_roles(id_user integer, new_login character varying, new_password character varying, role_ids integer[]) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    rows_affected INTEGER;
BEGIN
    -- Update the user with the specified id
    UPDATE users
    SET login = new_login, password = new_password
    WHERE id = id_user;

    -- Get the number of rows affected
    GET DIAGNOSTICS rows_affected = ROW_COUNT;

    -- Delete existing roles
	DELETE FROM users_roles WHERE user_id = id_user;

	-- Insert new roles
	INSERT INTO users_roles (user_id, role_id)
	SELECT id_user, role_id FROM unnest(role_ids) AS role_id;

    -- Return the number of rows affected
    RETURN rows_affected;
END;
$$;


ALTER FUNCTION public.update_user_with_roles(id_user integer, new_login character varying, new_password character varying, role_ids integer[]) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    login character varying NOT NULL,
    password character varying NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users_roles (
    user_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.users_roles OWNER TO postgres;

--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name) FROM stdin;
1	admin
2	user
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, login, password) FROM stdin;
2	lolo777.p@yandex.ru	$2a$10$NhqQauFsJ01PhWoQrzkyWOiU7GMMp.hy7xhcrbeokFSP9YJ5o9pPK
3	irina.shevchuk@wh-school.wb.ru	$2a$10$rrcZPNGDMfRD9nKEDSVvGuCKamTXQC1SpB32VE2Da5J3AklZIWqo.
4	artyom.krechun@wh-school.wb.ru	$2a$10$I.HXdsBRjFAxFDNQK3SIDujbE7SF6z8iJkanmiFNupxytVqVjmiAa
1	alexey.kosarev@wh-school.wb.ru	$2a$10$Ltz1aR7odRbfN2sAvnhZEeenyVNaUr1EUQzBFlv3AAG5gHwQt3dlq
\.


--
-- Data for Name: users_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users_roles (user_id, role_id) FROM stdin;
2	2
3	2
4	2
1	1
1	2
\.


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 4, true);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: users users_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_roles users_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_roles
    ADD CONSTRAINT users_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users_roles users_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_roles
    ADD CONSTRAINT users_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: users_roles users_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_roles
    ADD CONSTRAINT users_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

