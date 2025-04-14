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


let displayedTracks = [];

function getRecentTracks() {
    fetch('/recent-tracks')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('recent-tracks');

            if (data.error) {
                container.innerHTML = "<p>Erro ao obter faixas recentes.</p>";
                return;
            }

            const newTracks = [];
            const existingTrackIds = displayedTracks.map(track => track.name + track.artist + track.album); // Identificador mais robusto

            for (const track of data) {
                const trackId = track.name + track.artist + track.album;
                if (!existingTrackIds.includes(trackId)) {
                    newTracks.push(track);
                }
            }

            // Adiciona as novas músicas ao início do array displayedTracks
            displayedTracks = [...newTracks, ...displayedTracks].slice(0, 12);// Mantém no máximo 12

            // Renderiza a lista atualizada
            container.innerHTML = "";
            const list = document.createElement('ol');
            list.classList.add('songs-list');

            displayedTracks.forEach(track => {
                const songDiv = document.createElement('div');
                songDiv.classList.add('songs');
                songDiv.innerHTML = `
                    <img src="${track.image}" width="100%">
                    <div class="songname">
                        <strong>${track.name}</strong>
                    </div>
                    <div class="songdetails">
                        <p>Artista: ${track.artist}</p>
                        <p>Álbum: ${track.album}</p>
                    </div>
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

// Atualiza automaticamente a cada 20 segundos
setInterval(getRecentTracks, 20000);
getRecentTracks(); // executa na primeira vez
