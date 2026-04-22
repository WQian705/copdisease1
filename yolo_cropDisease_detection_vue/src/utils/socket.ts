import { io, Socket } from 'socket.io-client';
import { socketBaseUrl, socketPath } from '/@/utils/serviceUrl';

export class SocketService {
	private socket: Socket;

	constructor() {
		this.socket = io(socketBaseUrl, {
			path: socketPath,
			transports: ['polling'],
			reconnection: true,
		});
	}

	on(event: string, callback: (data: any) => void) {
		this.socket.on(event, (payload: any) => {
			callback(payload?.data ?? payload);
		});
	}

	emit(event: string, data: any) {
		this.socket.emit(event, data);
	}

	disconnect() {
		this.socket.disconnect();
	}
}
