document.addEventListener('DOMContentLoaded', function() { 
    const slidebox = document.querySelector('.slidebox');
    const titleElement = document.querySelector('.backgroundtext .text h1');
    const descriptionElement = document.querySelector('.backgroundtext .text p');
    const radioButtons = document.querySelectorAll('.carousel-radio');

    let slides = [];
    let currentIndex = 0;
    let interval;

    function updateSlide() {
        if (slides.length === 0) return;

        const currentSlide = slides[currentIndex];

        slidebox.style.backgroundImage = `url('${currentSlide.image}')`;
        slidebox.style.backgroundPosition = currentSlide.backgroundPosition || "0 8%"; // valor padrão

        titleElement.textContent = currentSlide.title;
        descriptionElement.textContent = currentSlide.description;

        document.getElementById(`slide${currentIndex + 1}`).checked = true;
    }

    function changeBackground() {
        if (slides.length === 0) return;
        currentIndex = (currentIndex + 1) % slides.length;
        updateSlide();
    }

    function setSlide(index) {
        clearInterval(interval);
        currentIndex = index;
        updateSlide();
        startAutoSlide();
    }

    function startAutoSlide() {
        interval = setInterval(changeBackground, 15000);
    }

    fetch(`https://xdchaves.github.io/carousel/carousel.json?t=${Date.now()}`)
    .then(response => response.json())
    .then(data => {
        // Transforma os destaques em uma lista
        slides = Object.values(data);
        updateSlide();
        startAutoSlide(); 

        radioButtons.forEach(button => {
            button.addEventListener('change', function() {
                setSlide(parseInt(this.dataset.index, 10));
            });
        });
    })
    .catch(error => console.error("Erro ao carregar os slides:", error));
});


function getRecentTracks() {
    fetch('/recent-tracks')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('recent-tracks');
            container.innerHTML = "";

            if (data.error) {
                container.innerHTML = "<p>Erro ao obter faixas recentes.</p>";
                return;
            }

            const list = document.createElement('ul');
            list.classList.add('songs-list');

            data.forEach(track => {
                const songDiv = document.createElement('div');
                songDiv.classList.add('songs');
                songDiv.innerHTML = `
                    <img src="${track.image}" width="100"><br>
                    <strong>${track.name}</strong><br>
                    Artista: ${track.artist}<br>
                    Álbum: ${track.album}<br><br>
                `;
                list.appendChild(songDiv);
            });

            container.appendChild(list);
        })
        .catch(error => {
            console.error("Erro ao carregar faixas:", error);
            document.getElementById('recent-tracks').innerHTML = "<p>Erro ao carregar faixas.</p>";
        });
}

// Atualiza automaticamente a cada 60 segundos
setInterval(getRecentTracks, 60000);
getRecentTracks(); // executa na primeira vez

