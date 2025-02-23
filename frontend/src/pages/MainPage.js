import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Container,
    Box,
    Typography,
    Button,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText,
    Paper
} from '@mui/material';
import { getUser, getRecords, createRecord, getChats, startChat } from '../api/api';
import ChatModal from '../components/ChatModal';

const MainPage = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [recordDialogOpen, setRecordDialogOpen] = useState(false);
    const [recordContent, setRecordContent] = useState('');
    const [records, setRecords] = useState([]);
    const [patientIdInput, setPatientIdInput] = useState('');
    const [recordViewDialogOpen, setRecordViewDialogOpen] = useState(false);

    // Chat related states for patients
    const [chats, setChats] = useState([]);
    const [chatModalOpen, setChatModalOpen] = useState(false);
    const [selectedChatId, setSelectedChatId] = useState(null);

    // Get logged-in user ID from localStorage
    const loggedInUserId = localStorage.getItem('userId');

    useEffect(() => {
        if (loggedInUserId) {
            getUser(loggedInUserId)
                .then(data => {
                    setUser(data);
                    // If user is a patient, load chat list
                    if (data.role_id === 2) {
                        loadChats();
                    }
                })
                .catch(err => {
                    console.error('Error fetching user:', err);
                });
        }
    }, [loggedInUserId]);

    const loadChats = () => {
        getChats()
            .then(data => {
                setChats(data.chats);
            })
            .catch(err => {
                console.error('Error fetching chats:', err);
            });
    };

    const handleOpenRecordDialog = () => {
        setRecordDialogOpen(true);
    };

    const handleCloseRecordDialog = () => {
        setRecordDialogOpen(false);
        setRecordContent('');
    };

    const handleCreateRecord = () => {
        const targetUserId = user.role_id === 2 ? loggedInUserId : patientIdInput;
        createRecord(targetUserId, recordContent)
            .then(newRecord => {
                console.log('Record created:', newRecord);
                handleCloseRecordDialog();
            })
            .catch(err => {
                console.error('Error creating record:', err);
            });
    };

    const handleViewRecords = () => {
        const targetUserId = user.role_id === 2 ? loggedInUserId : patientIdInput;
        getRecords(targetUserId)
            .then(data => {
                setRecords(data);
                setRecordViewDialogOpen(true);
            })
            .catch(err => {
                console.error('Error fetching records:', err);
            });
    };

    // Chat modal handlers
    const openChatModal = (chatId) => {
        setSelectedChatId(chatId);
        setChatModalOpen(true);
    };

    const handleStartNewChat = () => {
        startChat()
            .then(newChat => {
                const newChatId = newChat.chat_id || newChat.id;
                loadChats();
                openChatModal(newChatId);
            })
            .catch(err => {
                console.error('Error starting new chat:', err);
            });
    };

    // Logout handler
    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('userId');
        navigate('/login');
    };

    if (!user) {
        return <Typography>Loading...</Typography>;
    }

    return (
        <Container>
            {/* Beautified Header */}
            <Paper elevation={3} sx={{ padding: 2, marginBottom: 4, backgroundColor: '#1976d2', color: '#fff' }}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                        Welcome, {user.first_name} {user.last_name}
                    </Typography>
                    <Button variant="outlined" color="inherit" onClick={handleLogout}>
                        Logout
                    </Button>
                </Box>
                <Box mt={1}>
                    <Typography variant="subtitle1">
                        Role: {user.role_id === 2 ? 'Patient' : 'Doctor'}
                    </Typography>
                </Box>
            </Paper>

            {/* Main Content */}
            <Box display="flex">
                {user.role_id === 2 && (
                    <Box width="30%" borderRight="1px solid #ccc" paddingRight={2}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" marginBottom={2}>
                            <Typography variant="h6">Chats</Typography>
                            <Button variant="contained" color="primary" onClick={handleStartNewChat}>
                                Start New Chat
                            </Button>
                        </Box>
                        {chats.length > 0 ? (
                            chats.map((chat) => (
                                <Paper
                                    key={chat.chat_id}
                                    sx={{ padding: 1, marginBottom: 1, cursor: 'pointer' }}
                                    onClick={() => openChatModal(chat.chat_id)}
                                >
                                    <Typography>{chat.title}</Typography>
                                </Paper>
                            ))
                        ) : (
                            <Typography>No chats available.</Typography>
                        )}
                    </Box>
                )}
                <Box flexGrow={1} paddingLeft={user.role_id === 2 ? 2 : 0}>
                    <Paper elevation={2} sx={{ padding: 3, marginBottom: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Dashboard
                        </Typography>
                        <Typography variant="body1" gutterBottom>
                            Welcome to your dashboard. Here you can manage your records, chat with our agent, and access patient-related information.
                        </Typography>
                        {/* Record Buttons under Dashboard */}
                        {user.role_id === 1 ? (
                            <Box mt={2} display="flex" alignItems="center" gap={2}>
                                <TextField
                                    label="Patient ID"
                                    value={patientIdInput}
                                    onChange={(e) => setPatientIdInput(e.target.value)}
                                    variant="outlined"
                                    size="small"
                                />
                                <Button variant="contained" color="primary" onClick={handleViewRecords}>
                                    View Records
                                </Button>
                                <Button variant="contained" color="secondary" onClick={handleOpenRecordDialog}>
                                    Add Record
                                </Button>
                            </Box>
                        ) : (
                            <Box mt={2} display="flex" gap={2}>
                                <Button variant="contained" color="primary" onClick={handleViewRecords}>
                                    View Records
                                </Button>
                                <Button variant="contained" color="secondary" onClick={handleOpenRecordDialog}>
                                    Add Record
                                </Button>
                            </Box>
                        )}
                    </Paper>
                </Box>
            </Box>

            {/* Add Record Dialog */}
            <Dialog open={recordDialogOpen} onClose={handleCloseRecordDialog}>
                <DialogTitle>Add Record</DialogTitle>
                <DialogContent>
                    <TextField
                        label="Record Content"
                        fullWidth
                        multiline
                        rows={4}
                        value={recordContent}
                        onChange={(e) => setRecordContent(e.target.value)}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseRecordDialog}>Cancel</Button>
                    <Button onClick={handleCreateRecord} color="primary">
                        Save
                    </Button>
                </DialogActions>
            </Dialog>

            {/* View Records Dialog */}
            <Dialog open={recordViewDialogOpen} onClose={() => setRecordViewDialogOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Records</DialogTitle>
                <DialogContent>
                    <List>
                        {records.map(record => (
                            <ListItem key={record.id}>
                                <ListItemText
                                    primary={record.content}
                                    secondary={`${new Date(record.created_at).toLocaleString()} - Added by: ${record.added_by_role}`}
                                />
                            </ListItem>
                        ))}
                    </List>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setRecordViewDialogOpen(false)}>Close</Button>
                </DialogActions>
            </Dialog>

            {/* Chat Modal Popup */}
            <ChatModal open={chatModalOpen} onClose={() => setChatModalOpen(false)} chatId={selectedChatId} />
        </Container>
    );
};

export default MainPage;
