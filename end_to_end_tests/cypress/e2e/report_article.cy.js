describe('template spec', () => {

    beforeEach(() => {
        cy.fixture('user').then(user => {
            cy.register_user(user.username, user.password);
            cy.login_user(user.username, user.password);
        });
    });

    it('Report Article Test', () => {
        cy.fixture('article').then(article => {
            var tags_list;

            cy.visit('http://127.0.0.1:8000/user_app/create_article/');

            tags_list = '';
            article.tags.forEach((tag) => {
                if (tags_list === '') {
                    tags_list = tag;
                } else {
                    tags_list += ', ' + tag;
                }
            });

            cy.get('#id_title').type(article.title);
            cy.get('#id_tags').type(tags_list);

            cy.get('#id_form-0-title').type(article.steps[0].title);
            cy.get('#id_form-0-description1').type(article.steps[0].description1);
            cy.get('#id_form-0-description2').type(article.steps[0].description2);

            cy.get('#add-step-button').click();

            cy.get('#id_form-1-title').type(article.steps[1].title);
            cy.get('#id_form-1-description1').type(article.steps[1].description1);
            cy.get('#id_form-1-description2').type(article.steps[1].description2);

            cy.get('button[type="submit"]').click();

            cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

            cy.get('.card-body').should('contain', article.title);
            cy.get('.card-body').should('contain', 'Steps: 2');
            cy.fixture('user').then(user => {
                cy.get('.card-body').should('contain', user.username);
            });
            article.tags.forEach((tag) => {
                cy.get('.card-body').should('contain', '#' + tag);
            });
        });

        cy.get('button[name="view_article"]').click();
        cy.get('button[name="report_article"]').click();

        cy.get('#id_description').type('Description of the report');

        cy.get('#id_additional_file').selectFile('cypress/fixtures/favicon.png', {force: true});

        cy.get('button[name="submit_report"]').click();

        cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

        cy.fixture('user').then(user => {
            cy.get('.card-body').should('contain', user.username);
        });

        cy.get('.card-body').should('contain', 'Status: opened');

    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.fixture('user').then(user => {
            cy.cleanup_user(user.username);
        });
    });

});