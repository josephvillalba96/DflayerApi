module.exports = {
    apps: [
      {
        name: "DflayerApi",
  
        cwd: "/home/ubuntu/DflayerApi",
  
        script: ".venv/bin/uvicorn",
        args: "main:app --host 127.0.0.1 --port 8000",
  
        interpreter: "none",
        exec_mode: "fork",
  
        /* ============================
           CONTROL DE ARRANQUE
        ============================ */
  
        autorestart: true,              // Reinicia si el proceso muere
        restart_delay: 5000,             // Espera 5s entre reinicios
        max_restarts: 10,                // Máx 10 intentos seguidos
        min_uptime: "20s",               // Debe vivir 20s para considerarse estable
        exp_backoff_restart_delay: 1000, // Backoff exponencial (1s, 2s, 4s, 8s...)
  
        /* ============================
           CONTROL DE RECURSOS
        ============================ */
  
        max_memory_restart: "400M",      // Reinicia si se pasa de RAM
  
        /* ============================
           ROBUSTEZ
        ============================ */
  
        kill_timeout: 5000,              // Tiempo para cerrar limpio
        listen_timeout: 10000,           // Tiempo máximo de arranque
        shutdown_with_message: true,
  
        /* ============================
           VARIABLES DE ENTORNO
        ============================ */
  
        env: {
          PYTHONUNBUFFERED: "1",
          ENV: "production"
        },
  
        /* ============================
           LOGS
        ============================ */
  
        out_file: "/var/log/pm2/fastapi-out.log",
        error_file: "/var/log/pm2/fastapi-error.log",
        merge_logs: true,
        log_date_format: "YYYY-MM-DD HH:mm:ss"
      }
    ]
  };
  