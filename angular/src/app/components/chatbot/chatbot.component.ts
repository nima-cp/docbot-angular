import { Component, OnInit } from '@angular/core';
import { ChatApiService } from 'src/app/services/chat-api.service';
import axios from 'axios';

interface Message {
  id?: string;
  from?: 'user' | 'bot';
  message?: string;
  date?: Date;
}

interface Chat {
  chat_id?: number;
  title?: string;
  messages?: Message[];
}

interface Tokens {
  completion_tokens?: number;
  prompt_tokens?: number;
  total_tokens?: number;
  total_cost?: number;
}

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css'],
})
export class ChatbotComponent implements OnInit {
  chats: Chat[] = [];
  new_message: string = '';
  tokens: Tokens = {
    completion_tokens: 0,
    prompt_tokens: 0,
    total_tokens: 0,
    total_cost: 0,
  };
  selected_chat?: Chat = {};
  open_new_chat: boolean = false;
  errorMessage?: string = '';
  isLoading: boolean = false;

  selectedFile: File | null = null;

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  onUpload() {
    if (this.selectedFile) {
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      axios.post(`http://127.0.0.1:8080/upload`, formData).then(
        (response) => {
          console.log(response.data.message);
        },
        (error) => {
          console.error('Error uploading file:', error);
        }
      );
    }
  }
  /**
   * Service responsible for interacting with the chat-related APIs.
   * This service provides functions to call APIs for handling chat data.
   * @param {ChatApiService} ChatApiService - An instance of the ChatApiService used for making API calls.
   */
  constructor(private ChatApiService: ChatApiService) {}
  async ngOnInit() {
    await this.load_chat_history();
    this.selected_chat = this.get_selected_chat(this.selected_chat?.chat_id);
    if (!this.selected_chat) this.new_chat();
  }

  /**
   * Loads chat history from the ChatApiService and updates the UI with retrieved data.
   * If an error occurs, displays an error message to the user.
   * @throws {string} An error message if loading chat history fails.
   */
  private async load_chat_history(): Promise<void> {
    this.errorMessage = '';

    try {
      const response = await this.ChatApiService.loadChatHistory();
      this.chats = response.data.chats;

      if (!this.selected_chat?.chat_id) this.selected_chat = this.chats[0];
    } catch (error) {
      console.error('An error occurred while loading chat history:', error);
      this.errorMessage =
        'An error occurred while loading chat history. Please try again.';
    }
  }

  /**
   * Sends a message to the chatbot and handles various error scenarios.
   * Clears error message before sending a new message.
   * @throws {string} Error messages based on the type of error encountered.
   */
  async send_message(): Promise<void> {
    if (this.new_message.trim() === '') return;
    this.errorMessage = '';
    this.isLoading = true;

    this.selected_chat!.messages?.push({
      from: 'user',
      message: this.new_message,
    });
    this.scrollToBottom();
    const question = this.new_message;
    this.new_message = '';

    try {
      const response = await this.ChatApiService.getChatResponse(
        question,
        this.open_new_chat ? undefined : this.selected_chat?.chat_id
      );
      this.isLoading = false;
      console.log('response', response);

      this.open_new_chat = false;
      this.selected_chat!.chat_id = response.data.chat_id;
      this.tokens = response.data.tokens;

      await this.load_chat_history();
      this.selected_chat = this.get_selected_chat(this.selected_chat!.chat_id);

      this.scrollToBottom();
    } catch (error: any) {
      /**
       * Error Handling Block
       *
       * This block handles various error scenarios that might occur during the axios.post request.
       * It categorizes errors into different types based on their properties and provides relevant
       * error messages and console logs for each type.
       *
       * Types of Errors:
       * 1. Server Response Error: When the server responds with a non-successful status code.
       * 2. No Response Received: When the request was made, but no response was received.
       * 3. Request Setup Error: When an error occurred while setting up the request.
       */
      this.isLoading = false;

      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.log('Error Type 1: Server Response Error');
        console.log('Error Data:', error.response.data);
        console.log('Status Code:', error.response.status);
        console.log('Response Headers:', error.response.headers);
        this.errorMessage =
          'Server responded with an error: ' + error.response.data.error;
      } else if (error.request) {
        // The request was made but no response was received
        // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
        // http.ClientRequest in node.js
        console.log('Error Type 2: No Response Received');
        console.log('Request:', error.request);
        this.errorMessage = 'No response received from the server.';
      } else {
        // Something happened in setting up the request that triggered an Error
        console.log('Error Type 3: Request Setup Error');
        console.log('Error Message:', error.message);
        this.errorMessage = 'An error occurred while setting up the request.';
      }
      console.log('Request Config:', error.config);
    }
  }

  /**
   * Scrolls the chat container to the bottom to display the latest messages.
   */
  scrollToBottom() {
    const chatContainer = document.getElementById('messages_container');
    if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // restartDB() {
  //   console.log('DB Restarted!');
  //   // this.ChatApiService.restartDB()
  // }

  /**
   * Starts a new chat by initializing the 'selected_chat' with an initial message from the bot.
   * It sets the open_new_chat flag to true to pass undefined for the chat_id
   */
  new_chat(): void {
    this.open_new_chat = true;

    if (!this.selected_chat) {
      this.selected_chat = {};
    }

    this.selected_chat!.messages = [
      {
        from: 'bot',
        message: 'Ciao, come posso aiutarti?',
      },
    ];
  }

  /**
   * Changes the currently selected chat based on the clicked chat's ID.
   * Loads the chat history and updates the UI accordingly.
   * @param {number} clicked_chat_id - The ID of the clicked chat.
   */
  async change_chat(clicked_chat_id?: number): Promise<void> {
    this.open_new_chat = false;
    await this.load_chat_history();
    this.selected_chat!.chat_id = clicked_chat_id;
    this.selected_chat = this.get_selected_chat(this.selected_chat?.chat_id);
    console.log('Chat changed to:', this.selected_chat);
    this.scrollToBottom();
  }

  /**
   * Retrieves the selected chat based on its chat ID.
   * @param {number} chatId - The ID of the chat.
   * @returns {Chat | undefined} The selected chat object or undefined if not found.
   */
  get_selected_chat(chatId?: number): Chat | undefined {
    return this.chats.find((chat) => chat.chat_id === chatId);
  }

  /**
   * Sorts an array of chats based on the latest messages' timestamps.
   * @param {Chat[]} chats - An array of chats to be sorted.
   * @returns {Chat[]} The sorted array of chats.
   */
  sort_chats_by_latest_messages(chats: Chat[]): Chat[] {
    return chats.sort((a, b) => {
      const latestMessageA = a.messages?.length
        ? new Date(a.messages.at(-1)?.date ?? '')
        : undefined;
      const latestMessageB = b.messages?.length
        ? new Date(b.messages.at(-1)?.date ?? '')
        : undefined;

      if (latestMessageA && latestMessageB)
        return latestMessageB.getTime() - latestMessageA.getTime();
      else if (latestMessageA) return -1; // A has a message, but B doesn't
      else if (latestMessageB) return 1; // B has a message, but A doesn't

      return 0; // Both A and B don't have messages
    });
  }
}
