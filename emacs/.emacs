 ;; .emacs

;; timing
;;(require 'cl) ;; a rare necessary use of REQUIRE
;;(defvar *emacs-load-start* (current-time))


;; Start the emacs server only if another instance of the server is not running.
(require 'server)
(if (eq (server-running-p server-name) nil)
    (server-start))

(setq size-indication-mode t)  ;; show the file size
(setq column-number-mode t)    ;; display the column number
(setq scroll-step 1)           ;; line by line scrolling
(setq visible-bell t)          ;; disable the system beep
(setq inhibit-default-init t)  ;; disable loading of "default.el" at startup
(setq inhibit-splash-screen t) ;; disable splash screen
(setq transient-mark-mode t)   ;; enable visual feedback on selections

(setq python-check-command "flake8") ;; Trying to get pep8 going on elpy

(set-fringe-mode (cons 5 0))   ;; set fringe to only show on left
(set-scroll-bar-mode nil)      ;; remove the scroll bar
(tool-bar-mode -1)             ;; remove the toolbar
(fset 'yes-or-no-p 'y-or-n-p)  ;; Changes all yes/no questions to y/n type
(windmove-default-keybindings 'meta) ;; to move about windows using meta+arrow keys

;; Default-Browser = chrome
(setq browse-url-generic-program "google-chrome"
      browse-url-browser-function 'browse-url-generic)


;; "Prevent annoying \"Active processes exist\" query when you quit Emacs."
(defadvice save-buffers-kill-emacs (around no-query-kill-emacs activate)
  (flet ((process-list ())) ad-do-it))


;;Full screen with f11
;;Must install wmctrl
(defun switch-full-screen ()
  (interactive)
  (shell-command "wmctrl -r :ACTIVE: -btoggle,fullscreen"))
(global-set-key [f11] 'switch-full-screen)

;; highlight current line
(global-hl-line-mode 1)


;; set tab
(setq tab-width 3)

;;(global-set-key (kbd "TAB") 'self-insert-command);
(add-hook 'python-mode-hook '(lambda () (define-key python-mode-map "\C-m" 'newline-and-indent)))

;; default to better frame titles
;;(setq frame-title-format (concat  "%b - emacs@" (system-name)))
(setq frame-title-format "%b")

(setq diff-switches "-u")       ;; default to unified diffs

;; always end a file with a newline
;(setq require-final-newline 'query)

;;; Color theme based on Tango Palette. Created by danranx@gmail.com
;;; http://www.emacswiki.org/cgi-bin/emacs/color-theme-tango.el
(defun color-theme-tango ()
  "A color theme based on Tango Palette."
  (interactive)
  (color-theme-install
   '(color-theme-tango
     ((background-color . "#003366")
      (background-mode . dark)
      (border-color . "#888a85")
      (cursor-color . "#fce94f")
      (foreground-color . "#eeeeec")
      (mouse-color . "#8ae234"))
     ((help-highlight-face . underline)
      (ibuffer-dired-buffer-face . font-lock-function-name-face)
      (ibuffer-help-buffer-face . font-lock-comment-face)
      (ibuffer-hidden-buffer-face . font-lock-warning-face)
      (ibuffer-occur-match-face . font-lock-warning-face)
      (ibuffer-read-only-buffer-face . font-lock-type-face)
      (ibuffer-special-buffer-face . font-lock-keyword-face)
      (ibuffer-title-face . font-lock-type-face))
     (border ((t (:background "#888a85"))))
     (fringe ((f (:background "grey10"))))
     (mode-line ((t (:foreground "#eeeeec" :background "#555753"))))
     (region ((t (:background "#555753"))))
     (font-lock-builtin-face ((t (:foreground "#729fcf"))))
     (font-lock-comment-face ((t (:foreground "red"))))
     (font-lock-constant-face ((t (:foreground "#8ae234"))))
     (font-lock-doc-face ((t (:foreground "#888a85"))))
     (font-lock-keyword-face ((t (:foreground "#729fcf" :bold t))))
     ;; remove italic from strings
     (font-lock-string-face ((t (:foreground "#ad7fa8"))))
     (font-lock-type-face ((t (:foreground "#8ae234" :bold t))))
     (font-lock-variable-name-face ((t (:foreground "#eeeeec"))))
     (font-lock-warning-face ((t (:bold t :foreground "#f57900"))))
     (font-lock-function-name-face ((t (:foreground "#edd400" :bold t :italic t))))
     ;; ECB - matt added
     ;; see - http://ecb.sourceforge.net/docs/ecb-faces.html
     (ecb-default-highlight-face((t (:background "#75507b"))))
     ;; end ecb
     (comint-highlight-input ((t (:italic t :bold t))))
     (comint-highlight-prompt ((t (:foreground "#8ae234"))))
     (isearch ((t (:background "#f57900" :foreground "#2e3436"))))
     (isearch-lazy-highlight-face ((t (:foreground "#2e3436" :background "#e9b96e"))))
     (show-paren-match-face ((t (:foreground "#2e3436" :background "#73d216"))))
     (show-paren-mismatch-face ((t (:background "#ad7fa8" :foreground "#2e3436"))))
     (minibuffer-prompt ((t (:foreground "#729fcf" :bold t))))
     (info-xref ((t (:foreground "#729fcf"))))
     (info-xref-visited ((t (:foreground "#ad7fa8"))))
     )
   )
  )

(add-to-list 'load-path "~/.emacs.d")
(require 'dired-single)
;;(require 'auto-install)
(require 'color-theme)
;;(require 'remember)
;;(require 'psvn)

(require 'auto-complete)
(global-auto-complete-mode t)

;;(add-to-list 'load-path "~/.emacs.d/icicles")
;;(require 'icicles)
;;(icy-mode t)


;;(require 'pymacs)
;;(pymacs-load "ropemacs" "rope-")
;;(setq ropemacs-enable-autoimport t)

;;(Add-to-list 'load-path "~/.emacs.d/auto-complete-1.2")
;;(require 'auto-complete-config)
;;(add-to-list 'ac-dictionary-directories "~/.emacs.d/auto-complete-1.2/dict")
;;(ac-config-default)

;;(require 'ipython)

(color-theme-initialize)
(color-theme-tango)

;; csv mode
(add-to-list 'auto-mode-alist '("\\.[Cc][Ss][Vv]\\'" . csv-mode))
(autoload 'csv-mode "csv-mode" "Major mode for editing comma-separated value files." t)

;; matlab mode
(autoload 'matlab-mode "matlab.el" "Enter Matlab mode." t)
(setq auto-mode-alist (cons '("\\.m\\'" . matlab-mode) auto-mode-alist))
(autoload 'matlab-shell "matlab.el" "Interactive Matlab mode." t)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ECB
(add-to-list 'load-path "~/.emacs.d/ecb-2.32")
(require 'ecb-autoloads)



(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(cua-mode t nil (cua-base))
 '(ecb-options-version "2.32")
 '(show-paren-mode t)
 '(text-mode-hook (quote (text-mode-hook-identify)))
 '(truncate-lines t))

;; end of timing
;;(message "My .emacs loaded in %ds" (destructuring-bind (hi lo ms) (current-time)
;;                           (- (+ hi lo) (+ (first *emacs-load-start*) (second *emacs-load-start*)))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )



;; Keyboard macros and  shortcut customizations
(fset 'pdb_breakpoint
   "import ipdb; ipdb.set_trace()")
(fset 'qt_pdb_breakpoint
   "from PyQt4.QtCore import pyqtRemoveInputHook;	pyqtRemoveInputHook();import ipdb; ipdb.set_trace()")
(fset 'pyprint_variable
   "\355\C-kprint (\"\C-y: %s\" % \C-y)")
(fset 'remove_pdb_breakpoint
   [?\C-s ?i ?m ?p ?o ?r ?t ?  ?i ?p ?d ?b ?\; ?  ?i ?p ?d ?b ?. ?s ?e ?t ?_ ?t ?r ?a ?c ?e ?\( ?\) home ?\C-k ?\C-k])


(global-set-key (kbd "C-c C-M-p") 'pyprint_variable)
(global-set-key (kbd "C-c C-M-b") 'pdb_breakpoint)
(global-set-key (kbd "C-c C-M-q") 'qt_pdb_breakpoint)
(global-set-key (kbd "C-c C-M-S-b") 'remove_pdb_breakpoint)


;;Python Hook
;;Tab width
(add-hook 'python-mode-hook
      (lambda ()
        (setq indent-tabs-mode nil)
        (setq tab-width 4)
        (setq python-indent 4)))



(add-hook 'before-save-hook 'delete-trailing-whitespace)


;; Lets try to manipule backups
(setq backup-directory-alist `(("." . "~/.saves")))


;; Enable elpy
(package-initialize)
(elpy-enable)
