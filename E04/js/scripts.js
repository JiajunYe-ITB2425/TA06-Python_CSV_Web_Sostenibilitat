        document.addEventListener('DOMContentLoaded', function () {
            // Lazy load images
            const lazyImages = document.querySelectorAll('img.lazy');
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });

            lazyImages.forEach(img => {
                imageObserver.observe(img);
            });

            // Defer non-critical JavaScript
            const scriptsToDefer = document.querySelectorAll('script[data-defer]');
            scriptsToDefer.forEach(script => {
                const src = script.getAttribute('data-src');
                if (src) {
                    const newScript = document.createElement('script');
                    newScript.src = src;
                    document.body.appendChild(newScript);
                }
            });
        });

        // Función para aceptar cookies
        document.getElementById('accept-cookies').addEventListener('click', function () {
            document.getElementById('cookie-banner').style.display = 'none';
            document.body.style.overflow = 'auto'; // Desbloquear la página
        });

        // Función para rechazar cookies
        document.getElementById('reject-cookies').addEventListener('click', function () {
            alert("Debes aceptar las cookies para continuar navegando.");
        });
