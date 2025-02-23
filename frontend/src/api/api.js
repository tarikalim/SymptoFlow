import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

export const loginUser = async (userId, password) => {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        user_id: userId,
        password: password,
    });
    return response.data;
};

export const registerUser = async (firstName, lastName, roleId, password) => {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        first_name: firstName,
        last_name: lastName,
        role_id: roleId,
        password: password,
    });
    return response.data;
};

export const getUser = async (userId) => {
    const response = await axios.get(`${API_BASE_URL}/user/${userId}`);
    return response.data;
};

export const getRecords = async (userId) => {
    const response = await axios.get(`${API_BASE_URL}/records/${userId}`);
    return response.data;
};

export const createRecord = async (userId, content) => {
    const token = localStorage.getItem('token');
    const response = await axios.post(
        `${API_BASE_URL}/records/create/${userId}`,
        { content },
        {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );
    return response.data;
};

// Chat API functions
export const getChats = async () => {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE_URL}/chat/chats`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    return response.data;
};

export const startChat = async () => {
    const token = localStorage.getItem('token');
    const response = await axios.post(
        `${API_BASE_URL}/chat/start`,
        {},
        {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );
    return response.data;
};

export const getChatHistory = async (chatId) => {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_BASE_URL}/chat/${chatId}/history`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    return response.data;
};

export const sendQuestion = async (chatId, question) => {
    const token = localStorage.getItem('token');
    const response = await axios.post(
        `${API_BASE_URL}/chat/send-question`,
        { chat_id: chatId, question },
        {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );
    return response.data;
};
