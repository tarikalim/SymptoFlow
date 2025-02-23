import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    List,
    ListItem,
    ListItemText
} from '@mui/material';
import { getChatHistory, sendQuestion } from '../api/api';

const ChatModal = ({ open, onClose, chatId }) => {
    const [chatHistory, setChatHistory] = useState(null);
    const [question, setQuestion] = useState('');

    useEffect(() => {
        if (open && chatId) {
            fetchChatHistory();
        }
    }, [open, chatId]);

    const fetchChatHistory = () => {
        getChatHistory(chatId)
            .then(data => {
                setChatHistory(data);
            })
            .catch(err => {
                console.error("Error fetching chat history:", err);
            });
    };

    const handleSendQuestion = () => {
        if (!question) return;
        sendQuestion(chatId, question)
            .then(() => {
                fetchChatHistory();
                setQuestion('');
            })
            .catch(err => {
                console.error("Error sending question:", err);
            });
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
            <DialogTitle>Chat - ID: {chatId}</DialogTitle>
            <DialogContent dividers>
                {chatHistory ? (
                    <List>
                        {chatHistory.history && chatHistory.history.length > 0 ? (
                            chatHistory.history.map((msg, index) => (
                                <ListItem key={index}>
                                    <ListItemText primary={`Q: ${msg.question}`} secondary={`A: ${msg.answer}`} />
                                </ListItem>
                            ))
                        ) : (
                            <ListItem>
                                <ListItemText primary="No messages yet." />
                            </ListItem>
                        )}
                    </List>
                ) : (
                    "Loading chat history..."
                )}
                <TextField
                    label="Your Question"
                    fullWidth
                    multiline
                    rows={2}
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    margin="normal"
                />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
                <Button onClick={handleSendQuestion} variant="contained" color="primary">
                    Send
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default ChatModal;
