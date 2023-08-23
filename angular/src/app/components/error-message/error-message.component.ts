import { Component, Input, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-error-message',
  templateUrl: './error-message.component.html',
  styleUrls: ['./error-message.component.css'],
})
export class ErrorMessageComponent {
  @Input() errorMessage?: string;
  showErrorMessage: boolean = true;

  ngOnChanges(changes: SimpleChanges) {
    if (changes && this.errorMessage) {
      this.showErrorMessage = true;
    } else {
      this.showErrorMessage = false;
    }
  }
  error_message_close() {
    this.showErrorMessage = false;
    this.errorMessage = '';
  }
}
