import { Injectable } from '@angular/core';
import axios from 'axios';
import { environment } from '../environments/environment';

/**
 * This service provides APIs calling functions for handling the chat data.
 */
@Injectable({
  providedIn: 'root',
})
export class ChatApiService {
  private API_URL = environment.API_URL;

  constructor() {}

  /**
   * Loads the chat history from the database.
   * @returns {Promise<any>} A Promise containing the response from the API call.
   */
  loadChatHistory() {
    return axios.get(`${this.API_URL}/load_chats`);
  }

  /**
   * Sends a message to the chatbot and retrieves its response.
   * @param {string} message - The user's message to send to the chatbot.
   * @param {number} chat_id - (Optional) Chat ID if continuing an existing chat.
   * @returns A Promise containing the response from the API call. The response object contains the chat ID, the chatbot response, all the messages, and all the tokens used for this message.
   */
  getChatResponse(message: string, chat_id?: number) {
    return axios.post(`${this.API_URL}/chatbot`, {
      chat_id,
      message,
    });
  }
}
