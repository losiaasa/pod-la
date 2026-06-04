// 1. FUNGSI UNTUK PINDAH HALAMAN
function showPage(pageId) {
    // Sembunyikan semua halaman terlebih dahulu
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.remove('active');
    });

    // Tampilkan halaman yang dipilih berdasarkan ID
    const activePage = document.getElementById(pageId);
    if (activePage) {
        activePage.classList.add('active');
    }
}

// 2. FUNGSI UNTUK MEMBUKA POP-UP PEMBAYARAN
function openPayment(productName, price) {
    const modal = document.getElementById('payment-modal');
    const modalText = document.getElementById('modal-product-name');
    
    // Set text nama produk dan harga di dalam modal
    modalText.innerHTML = `Anda memilih: ${productName} <br> <span style="color: #e74c3c;">Total: Rp ${price.toLocaleString('id-ID')}</span>`;
    
    // Tampilkan modal
    modal.style.display = 'flex';
}

// 3. FUNGSI UNTUK MENUTUP POP-UP PEMBAYARAN
function closePayment() {
    const modal = document.getElementById('payment-modal');
    modal.style.display = 'none';
}

// 4. FUNGSI PROSES PEMBAYARAN (SIMULASI BERHASIL)
function processPayment(event) {
    event.preventDefault(); // Mencegah halaman reload saat submit
    
    alert('Terima kasih! Pembayaran Anda berhasil diproses. Kami akan segera menghubungi Anda.');
    
    // Tutup modal dan reset form
    closePayment();
    document.getElementById('payment-form').reset();
}

// Menutup modal jika user mengklik area di luar kotak modal
window.onclick = function(event) {
    const modal = document.getElementById('payment-modal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}