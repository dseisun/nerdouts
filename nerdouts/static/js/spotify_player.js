/**
 * Spotify Web Playback SDK Wrapper
 *
 * This module provides a clean interface to control Spotify playback
 * via the Web Playback SDK. It handles authentication, initialization,
 * and provides methods for pause/play/resume functionality.
 */

class SpotifyPlayer {
    constructor() {
        this.player = null;
        this.accessToken = null;
        this.refreshToken = null;
        this.isReady = false;
        this.isInitializing = false;
        this.currentTrackUri = null;
        this.deviceId = null;
        this.currentTrack = null;
        this.isPlaying = false;
    }

    /**
     * Initialize the Spotify player
     * Loads the SDK, checks for stored token, and creates player instance
     */
    async initialize() {
        if (this.isInitializing || this.isReady) {
            return;
        }

        this.isInitializing = true;

        try {
            // Check if user is authenticated
            if (!this.checkAuthentication()) {
                console.log('SpotifyPlayer: No authentication token found, redirecting to login...');
                window.location.href = '/spotify/login';
                return;
            }

            // Load Spotify Web Playback SDK
            await this.loadSDK();

            // Wait for SDK to be ready
            await this.waitForSDK();

            // Create player instance
            this.createPlayer();

            // Connect to player
            await this.connectPlayer();

            this.isReady = true;
            console.log('SpotifyPlayer: Initialized successfully');
            return true;
        } catch (error) {
            console.error('SpotifyPlayer: Initialization failed:', error);
            this.isInitializing = false;
            throw error;
        }
    }

    /**
     * Check if access token is stored in localStorage
     */
    checkAuthentication() {
        this.accessToken = localStorage.getItem('spotify_access_token');
        this.refreshToken = localStorage.getItem('spotify_refresh_token');

        if (!this.accessToken) {
            console.log('SpotifyPlayer: No access token found');
            return false;
        }

        console.log('SpotifyPlayer: Access token found, checking validity...');
        return true;
    }

    /**
     * Dynamically load the Spotify Web Playback SDK
     */
    loadSDK() {
        return new Promise((resolve, reject) => {
            // Check if SDK already loaded
            if (window.Spotify && window.Spotify.Player) {
                resolve();
                return;
            }

            // Set up the callback BEFORE loading the script
            // This is required by Spotify's SDK
            window.onSpotifyWebPlaybackSDKReady = () => {
                console.log('Spotify Web Playback SDK Ready');
                resolve();
            };

            const script = document.createElement('script');
            script.src = 'https://sdk.scdn.co/spotify-player.js';
            script.async = true;

            script.onerror = () => {
                reject(new Error('Failed to load Spotify Web Playback SDK'));
            };

            document.head.appendChild(script);

            // Timeout in case SDK never calls the callback
            setTimeout(() => {
                if (!window.Spotify || !window.Spotify.Player) {
                    reject(new Error('Spotify SDK did not initialize within 10 seconds'));
                }
            }, 10000);
        });
    }

    /**
     * Wait for Spotify SDK to be available (with callback trigger)
     * This is now mostly handled by loadSDK's callback, but we keep it for safety
     */
    waitForSDK(maxAttempts = 100) {
        return new Promise((resolve, reject) => {
            let attempts = 0;

            const checkSDK = () => {
                if (window.Spotify && window.Spotify.Player) {
                    resolve();
                } else if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(checkSDK, 100);
                } else {
                    reject(new Error('Spotify SDK did not load in time'));
                }
            };

            checkSDK();
        });
    }

    /**
     * Create the Spotify player instance
     */
    createPlayer() {
        if (!window.Spotify || !window.Spotify.Player) {
            throw new Error('Spotify Player SDK not available');
        }

        this.player = new window.Spotify.Player({
            name: 'Nerdouts Workout Player',
            getOAuthToken: (cb) => cb(this.accessToken),
            volume: 0.5
        });

        // Set up event listeners
        // The 'ready' event fires when the SDK is ready and contains the device_id
        this.player.addListener('ready', ({ device_id }) => {
            this.deviceId = device_id;
            console.log('SpotifyPlayer: Ready event - Device ID:', device_id);
        });

        this.player.addListener('player_state_changed', (state) => {
            // Store current track info for display (without making API calls)
            if (state && state.track_window && state.track_window.current_track) {
                this.currentTrack = state.track_window.current_track;
                this.isPlaying = !state.paused;

                // Dispatch custom event so the UI can listen to updates
                window.dispatchEvent(new CustomEvent('spotifyTrackChanged', {
                    detail: {
                        track: this.currentTrack,
                        isPlaying: this.isPlaying
                    }
                }));
            }
        });

        this.player.addListener('initialization_error', ({ message }) => {
            console.error('SpotifyPlayer: Initialization error:', message);
        });

        this.player.addListener('authentication_error', ({ message }) => {
            console.error('SpotifyPlayer: Authentication error:', message);
            // Token expired, redirect to login
            localStorage.removeItem('spotify_access_token');
            window.location.href = '/spotify/login';
        });

        this.player.addListener('account_error', ({ message }) => {
            console.error('SpotifyPlayer: Account error:', message);
        });
    }

    /**
     * Connect the player to Spotify
     * The 'ready' event listener will fire and set this.deviceId
     */
    connectPlayer() {
        return new Promise((resolve, reject) => {
            const connectTimeout = setTimeout(() => {
                reject(new Error('Player connection timeout'));
            }, 10000);

            this.player.connect().then((success) => {
                clearTimeout(connectTimeout);
                if (success) {
                    console.log('SpotifyPlayer: Connected to Spotify');
                    resolve();
                } else {
                    reject(new Error('Failed to connect player'));
                }
            });
        });
    }

    /**
     * Play a Spotify track or playlist
     * @param {string} uri - Spotify URI (spotify:track:xxx or spotify:playlist:xxx)
     * @param {object} options - Optional playback options
     */
    async play(uri, options = {}) {
        if (!this.isReady) {
            throw new Error('SpotifyPlayer not initialized');
        }

        try {
            const deviceId = await this.getDeviceId();

            const playOptions = {
                uris: Array.isArray(uri) ? uri : [uri],
                ...options
            };

            const response = await fetch(
                `https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`,
                {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(playOptions)
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to play: ${response.statusText}`);
            }

            this.currentTrackUri = uri;
            console.log('SpotifyPlayer: Playing track');
        } catch (error) {
            console.error('SpotifyPlayer: Play error:', error);
            throw error;
        }
    }

    /**
     * Pause playback
     */
    async pause() {
        if (!this.isReady) {
            throw new Error('SpotifyPlayer not initialized');
        }

        try {
            const deviceId = await this.getDeviceId();

            const response = await fetch(
                `https://api.spotify.com/v1/me/player/pause?device_id=${deviceId}`,
                {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                }
            );

            if (!response.ok && response.status !== 204) {
                throw new Error(`Failed to pause: ${response.statusText}`);
            }

            console.log('SpotifyPlayer: Paused');
        } catch (error) {
            console.error('SpotifyPlayer: Pause error:', error);
            throw error;
        }
    }

    /**
     * Resume playback
     */
    async resume() {
        if (!this.isReady) {
            throw new Error('SpotifyPlayer not initialized');
        }

        try {
            const deviceId = await this.getDeviceId();

            const response = await fetch(
                `https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`,
                {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({})
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to resume: ${response.statusText}`);
            }

            console.log('SpotifyPlayer: Resumed');
        } catch (error) {
            console.error('SpotifyPlayer: Resume error:', error);
            throw error;
        }
    }

    /**
     * Skip to next track
     */
    async next() {
        if (!this.isReady) {
            throw new Error('SpotifyPlayer not initialized');
        }

        try {
            const deviceId = await this.getDeviceId();

            const response = await fetch(
                `https://api.spotify.com/v1/me/player/next?device_id=${deviceId}`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                }
            );

            if (!response.ok && response.status !== 204) {
                throw new Error(`Failed to skip to next: ${response.statusText}`);
            }

            console.log('SpotifyPlayer: Skipped to next track');
        } catch (error) {
            console.error('SpotifyPlayer: Next error:', error);
            throw error;
        }
    }

    /**
     * Go to previous track
     */
    async previous() {
        if (!this.isReady) {
            throw new Error('SpotifyPlayer not initialized');
        }

        try {
            const deviceId = await this.getDeviceId();

            const response = await fetch(
                `https://api.spotify.com/v1/me/player/previous?device_id=${deviceId}`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                }
            );

            if (!response.ok && response.status !== 204) {
                throw new Error(`Failed to go to previous: ${response.statusText}`);
            }

            console.log('SpotifyPlayer: Went to previous track');
        } catch (error) {
            console.error('SpotifyPlayer: Previous error:', error);
            throw error;
        }
    }

    /**
     * Toggle between play and pause
     */
    async togglePlayPause() {
        if (!this.isReady) {
            throw new Error('SpotifyPlayer not initialized');
        }

        try {
            const state = await this.getCurrentState();

            if (state && state.is_playing) {
                await this.pause();
            } else {
                await this.resume();
            }
        } catch (error) {
            console.error('SpotifyPlayer: Toggle play/pause error:', error);
            throw error;
        }
    }

    /**
     * Get the device ID for this player
     * The device ID is captured when the first player_state_changed event fires
     * @private
     */
    async getDeviceId() {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            const maxAttempts = 50;

            const checkDeviceId = () => {
                if (this.deviceId) {
                    console.log('SpotifyPlayer: Using device ID:', this.deviceId);
                    resolve(this.deviceId);
                } else if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(checkDeviceId, 100);
                } else {
                    reject(new Error('Could not get device ID from Spotify player after 5 seconds'));
                }
            };

            checkDeviceId();
        });
    }

    /**
     * Get available Spotify devices
     */
    async getAvailableDevices() {
        try {
            const response = await fetch('https://api.spotify.com/v1/me/player/devices', {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            if (response.status === 401) {
                console.error('SpotifyPlayer: Access token expired or invalid');
                // Token is invalid, redirect to login
                localStorage.removeItem('spotify_access_token');
                localStorage.removeItem('spotify_refresh_token');
                window.location.href = '/spotify/login';
                throw new Error('Access token expired, redirecting to login');
            }

            if (!response.ok) {
                throw new Error(`Failed to get devices: ${response.statusText}`);
            }

            const data = await response.json();
            return data.devices || [];
        } catch (error) {
            console.error('SpotifyPlayer: Get devices error:', error);
            return [];
        }
    }

    /**
     * Get current playback state
     */
    async getCurrentState() {
        try {
            const response = await fetch('https://api.spotify.com/v1/me/player/currently-playing', {
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to get state: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('SpotifyPlayer: Get state error:', error);
            return null;
        }
    }

    /**
     * Set volume (0.0 to 1.0)
     */
    async setVolume(volume) {
        if (!this.isReady) {
            throw new Error('SpotifyPlayer not initialized');
        }

        if (volume < 0 || volume > 1) {
            throw new Error('Volume must be between 0.0 and 1.0');
        }

        try {
            const deviceId = await this.getDeviceId();
            const percent = Math.round(volume * 100);

            const response = await fetch(
                `https://api.spotify.com/v1/me/player/volume?volume_percent=${percent}&device_id=${deviceId}`,
                {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                }
            );

            if (!response.ok && response.status !== 204) {
                throw new Error(`Failed to set volume: ${response.statusText}`);
            }

            console.log(`SpotifyPlayer: Volume set to ${percent}%`);
        } catch (error) {
            console.error('SpotifyPlayer: Set volume error:', error);
            throw error;
        }
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!localStorage.getItem('spotify_access_token');
    }

    /**
     * Logout user
     */
    logout() {
        localStorage.removeItem('spotify_access_token');
        localStorage.removeItem('spotify_refresh_token');
        localStorage.removeItem('spotify_expires_in');
        this.isReady = false;
        if (this.player) {
            this.player.disconnect();
        }
    }
}
