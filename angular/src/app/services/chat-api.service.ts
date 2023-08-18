import { Injectable } from '@angular/core';
import axios from 'axios';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ChatApiService {
  private API_URL = environment.API_URL;

  constructor() {}

  loadChatHistory() {
    return axios.get(`${this.API_URL}/load_chats`);
  }

  getChatResponse(message: string, chat_id?: number) {
    return axios.post(`${this.API_URL}/chatbot_test`, {
      chat_id,
      question: message,
    });
  }
}
