(() => {
  const toastStack = document.getElementById('toast-stack')
  const icons = {
    success: '✅',
    error: '⚠️',
    info: 'ℹ️',
  }
  window.pushToast = (message, variant = 'success') => {
    if (!toastStack) return alert(message)
    const toast = document.createElement('div')
    toast.className = 'toast'
    toast.dataset.variant = variant.includes('error') ? 'error' : variant
    toast.innerHTML = `<span class="toast-icon">${icons[toast.dataset.variant] || 'ℹ️'}</span><span>${message}</span>`
    toastStack.appendChild(toast)
    requestAnimationFrame(() => toast.classList.add('opacity-100'))
    setTimeout(() => {
      toast.style.opacity = 0
      toast.addEventListener('transitionend', () => toast.remove(), { once: true })
    }, 3500)
  }

  // Intercepteur global pour gérer la perte d'accès pendant qu'on est sur la page
  const originalFetch = window.fetch?.bind(window)
  if (originalFetch) {
    window.fetch = (input, init) => originalFetch(input, init).then((res) => {
      if (res && (res.status === 403 || res.status === 404)) {
        // Accès révoqué ou ressource supprimée pendant la session
        window.pushToast("Vos droits d'accès à ce contenu ont été révoqués.", 'error')
        // Redirection douce vers la liste des tableaux
        setTimeout(() => { try { window.location.href = '/boards/'; } catch (_) {} }, 1200)
      }
      return res
    }).catch((err) => {
      window.pushToast('Erreur de connexion. Veuillez vérifier votre accès à Internet.', 'error')
      throw err
    })
  }

  document.querySelectorAll('[data-collapse-toggle]').forEach(button => {
    button.addEventListener('click', () => {
      const list = button.closest('[data-list-id]')
      list?.classList.toggle('list-collapsed')
    })
  })

  const onboarding = document.querySelector('[data-onboarding]')
  if (onboarding) {
    let index = 0
    const slides = onboarding.querySelectorAll('[data-slide]')
    const update = () => {
      slides.forEach((slide, i) => {
        slide.classList.toggle('opacity-100', i === index)
        slide.classList.toggle('opacity-0', i !== index)
        slide.classList.toggle('pointer-events-none', i !== index)
      })
    }
    onboarding.querySelector('[data-prev]')?.addEventListener('click', () => {
      index = (index - 1 + slides.length) % slides.length
      update()
    })
    onboarding.querySelector('[data-next]')?.addEventListener('click', () => {
      index = (index + 1) % slides.length
      update()
    })
    setInterval(() => {
      index = (index + 1) % slides.length
      update()
    }, 5000)
    update()
  }

  document.querySelectorAll('[data-tooltip]').forEach(el => {
    el.classList.add('tooltip')
    el.setAttribute('tabindex', '0')
  })
})()
