import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../api/api';
import { Button, TextField, Typography, Container } from '@mui/material';

const LoginPage = () => {
    const [userId, setUserId] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const data = await loginUser(parseInt(userId, 10), password);
            localStorage.setItem('token', data.token);
            localStorage.setItem('userId', userId);
            navigate('/');
        } catch (error) {
            console.error('Login error:', error);
        }
    };

    return (
        <Container maxWidth="xs">
            <Typography variant="h4" component="h1" align="center" gutterBottom>
                Login
            </Typography>
            <form onSubmit={handleLogin}>
                <TextField
                    label="User ID"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    required
                />
                <TextField
                    label="Password"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <Button type="submit" variant="contained" color="primary" fullWidth>
                    Login
                </Button>
            </form>
            <Typography variant="body2" align="center" style={{ marginTop: 16 }}>
                You can register here.{' '}
                <Button onClick={() => navigate('/register')} color="secondary">
                    Register
                </Button>
            </Typography>
        </Container>
    );
};

export default LoginPage;
