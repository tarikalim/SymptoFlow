import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../api/api';
import { Button, TextField, Typography, Container, MenuItem } from '@mui/material';

const roles = [
    { value: 1, label: 'Doctor' },
    { value: 2, label: 'Patient' },
];

const RegisterPage = () => {
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [roleId, setRoleId] = useState(2); // Default role: Patient
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            const data = await registerUser(firstName, lastName, roleId, password);
            console.log('Registration successful:', data);
            navigate('/login');
        } catch (error) {
            console.error('Registration error:', error);
        }
    };

    return (
        <Container maxWidth="xs">
            <Typography variant="h4" component="h1" align="center" gutterBottom>
                Register
            </Typography>
            <form onSubmit={handleRegister}>
                <TextField
                    label="First Name"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                />
                <TextField
                    label="Last Name"
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                />
                <TextField
                    select
                    label="Role"
                    value={roleId}
                    onChange={(e) => setRoleId(parseInt(e.target.value, 10))}
                    variant="outlined"
                    fullWidth
                    margin="normal"
                    required
                >
                    {roles.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                            {option.label}
                        </MenuItem>
                    ))}
                </TextField>
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
                    Register
                </Button>
            </form>
            <Typography variant="body2" align="center" style={{ marginTop: 16 }}>
                Already have an account?{' '}
                <Button onClick={() => navigate('/login')} color="secondary">
                    Login
                </Button>
            </Typography>
        </Container>
    );
};

export default RegisterPage;
